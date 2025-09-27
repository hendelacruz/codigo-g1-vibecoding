import React, { useState } from 'react';
import { usePermissionsCorrect } from '../../../hooks/usePermissionsCorrect';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
  activeModule?: string;
  onModuleChange?: (module: string) => void;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  description: string;
  requiredPermissions?: string[];
  requiredRoles?: string[];
  subItems?: NavigationItem[];
}

const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: '📊',
    description: 'Vista general del sistema'
  },
  {
    id: 'auth',
    label: 'Autenticación',
    icon: '🔐',
    description: 'Gestión de usuarios y permisos',
    requiredRoles: ['Administradores']
  },
  {
    id: 'inventory',
    label: 'Compras / Inventario',
    icon: '📦',
    description: 'Gestión de compras e inventario',
    requiredPermissions: ['inventory.view_dispositivo'],
    requiredRoles: ['Administradores', 'Supervisores', 'Técnicos', 'Operadores'],
    subItems: [
      {
        id: 'gps',
        label: 'Dispositivos GPS',
        icon: '🛰️',
        description: 'Gestión de dispositivos GPS',
        requiredPermissions: ['inventory.view_dispositivo'],
        requiredRoles: ['Administradores', 'Supervisores', 'Técnicos', 'Operadores']
      },
      {
        id: 'simcards',
        label: 'Tarjetas SIM',
        icon: '📱',
        description: 'Gestión de tarjetas SIM',
        requiredPermissions: ['inventory.view_dispositivo'],
        requiredRoles: ['Administradores', 'Supervisores', 'Técnicos', 'Operadores']
      },
      {
        id: 'otros-productos',
        label: 'Otros Productos',
        icon: '📋',
        description: 'Gestión de otros productos',
        requiredPermissions: ['inventory.view_dispositivo'],
        requiredRoles: ['Administradores', 'Supervisores', 'Técnicos', 'Operadores']
      }
    ]
  },
  {
    id: 'clientes',
    label: 'Clientes',
    icon: '👥',
    description: 'Gestión de clientes',
    requiredRoles: ['Administradores', 'Supervisores']
  },
  {
    id: 'proveedores',
    label: 'Proveedores',
    icon: '🏢',
    description: 'Gestión de proveedores',
    requiredRoles: ['Administradores', 'Supervisores']
  },
  {
    id: 'unidades',
    label: 'Unidades',
    icon: '🚗',
    description: 'Gestión de unidades vehiculares',
    requiredRoles: ['Administradores', 'Supervisores']
  },
  {
    id: 'services',
    label: 'Servicios',
    icon: '🔧',
    description: 'Gestión de servicios técnicos',
    requiredPermissions: ['services.view_servicio'],
    requiredRoles: ['Administradores', 'Supervisores', 'Técnicos']
  },
  {
    id: 'sales',
    label: 'Ventas',
    icon: '💰',
    description: 'Módulo de ventas',
    requiredRoles: ['Administradores', 'Supervisores']
  },
  {
    id: 'reports',
    label: 'Reportes',
    icon: '📈',
    description: 'Reportes y análisis',
    requiredRoles: ['Administradores', 'Supervisores']
  }
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  isOpen = true, 
  onClose, 
  activeModule = 'dashboard',
  onModuleChange 
}) => {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set(['inventory']));
  const { hasPermission, hasRole } = usePermissionsCorrect();

  // Function to check if user has access to a navigation item
  const checkItemPermissions = (item: NavigationItem): boolean => {
    // Check permissions
    if (item.requiredPermissions && item.requiredPermissions.length > 0) {
      const hasRequiredPermission = item.requiredPermissions.some(permission => 
        hasPermission(permission)
      );
      if (!hasRequiredPermission) return false;
    }

    // Check roles
    if (item.requiredRoles && item.requiredRoles.length > 0) {
      const hasRequiredRole = item.requiredRoles.some(role => hasRole(role));
      if (!hasRequiredRole) return false;
    }

    return true;
  };

  // Filter navigation items based on permissions and roles
  const filteredNavigationItems = navigationItems.filter(item => {
    // Check if the main item has permissions
    const hasMainItemAccess = checkItemPermissions(item);
    
    // If item has sub-items, check if any sub-item is accessible
    if (item.subItems && item.subItems.length > 0) {
      const accessibleSubItems = item.subItems.filter(subItem => checkItemPermissions(subItem));
      // Show parent item if it has accessible sub-items
      return accessibleSubItems.length > 0;
    }
    
    // For items without sub-items, show only if user has access
    return hasMainItemAccess;
  }).map(item => {
    // Filter sub-items based on permissions
    if (item.subItems && item.subItems.length > 0) {
      return {
        ...item,
        subItems: item.subItems.filter(subItem => checkItemPermissions(subItem))
      };
    }
    return item;
  });

  const handleItemClick = (itemId: string, hasSubItems: boolean = false) => {
    if (hasSubItems) {
      toggleExpansion(itemId);
      // Para el inventario, también activar el módulo directamente
      if (itemId === 'inventory') {
        onModuleChange?.(itemId);
      }
    } else {
      onModuleChange?.(itemId);
    }
  };

  const toggleExpansion = (itemId: string, e?: React.MouseEvent) => {
    if (e) {
      e.stopPropagation();
    }
    
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  return (
    <aside className={`
      fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-lg transition-all duration-300 ease-in-out z-50
      ${isOpen ? 'w-64' : 'w-16'}
      flex flex-col
    `}>
      <div className="flex-1 overflow-y-auto">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            {isOpen ? (
              <h2 className="text-lg font-semibold text-gray-800">
                Sistema GPS
              </h2>
            ) : (
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">SG</span>
              </div>
            )}
            <button
              onClick={onClose}
              className="p-1 rounded-md hover:bg-gray-100 transition-colors"
              title={isOpen ? 'Contraer sidebar' : 'Expandir sidebar'}
            >
              {isOpen ? (
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <nav className="p-4">
          <ul className="space-y-2">
            {filteredNavigationItems.map((item) => (
              <li key={item.id}>
                <div className={`
                  w-full flex items-center rounded-lg transition-all duration-200
                  ${(activeModule === item.id || (item.subItems && item.subItems.some(sub => sub.id === activeModule)))
                    ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                    : 'text-gray-600 hover:bg-gray-100'
                  }
                `}>
                  <button
                    onClick={() => handleItemClick(item.id, !!item.subItems)}
                    onMouseEnter={() => setHoveredItem(item.id)}
                    onMouseLeave={() => setHoveredItem(null)}
                    className="flex-1 flex items-center p-3 text-left"
                    title={!isOpen ? item.label : undefined}
                  >
                    <span className="text-xl mr-3 flex-shrink-0">{item.icon}</span>
                    {isOpen && (
                      <div className="flex-1 text-left">
                        <div className="font-medium">{item.label}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          {item.description}
                        </div>
                      </div>
                    )}
                    {(activeModule === item.id || (item.subItems && item.subItems.some(sub => sub.id === activeModule))) && isOpen && !item.subItems && (
                      <div className="w-2 h-2 bg-blue-500 rounded-full ml-2"></div>
                    )}
                  </button>
                  {item.subItems && isOpen && (
                    <button
                      onClick={(e) => toggleExpansion(item.id, e)}
                      className="p-1 hover:bg-gray-200 rounded transition-colors ml-2 mr-3"
                    >
                      <span className={`transform transition-transform duration-200 ${
                        expandedItems.has(item.id) ? 'rotate-90' : ''
                      }`}>
                        ▶
                      </span>
                    </button>
                  )}
                </div>
                
                {item.subItems && isOpen && expandedItems.has(item.id) && (
                  <ul className="ml-6 mt-2 space-y-1">
                    {item.subItems.map((subItem) => (
                      <li key={subItem.id}>
                        <button
                          onClick={() => handleItemClick(subItem.id)}
                          onMouseEnter={() => setHoveredItem(subItem.id)}
                          onMouseLeave={() => setHoveredItem(null)}
                          className={`
                            w-full flex items-center p-2 rounded-md transition-all duration-200 text-sm
                            ${activeModule === subItem.id 
                              ? 'bg-blue-100 text-blue-800 border border-blue-300' 
                              : 'text-gray-600 hover:bg-gray-100'
                            }
                          `}
                          title={subItem.label}
                        >
                          <span className="text-sm mr-2">{subItem.icon}</span>
                          <div className="flex-1 text-left">
                            <div className="font-medium">{subItem.label}</div>
                          </div>
                          {activeModule === subItem.id && (
                            <div className="w-1.5 h-1.5 bg-blue-600 rounded-full"></div>
                          )}
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          {isOpen && (
            <div className="text-xs text-gray-500 text-center">
              Sistema de Gestión GPS v1.0
            </div>
          )}
        </div>
      </div>

      {!isOpen && hoveredItem && (
        <div className="fixed left-20 bg-gray-800 text-white px-2 py-1 rounded text-sm z-50 pointer-events-none">
          {navigationItems.find(item => item.id === hoveredItem)?.label}
        </div>
      )}
    </aside>
  );
};