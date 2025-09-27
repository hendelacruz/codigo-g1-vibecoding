import React from 'react'

interface GeneralDashboardProps {
  onModuleSelect?: (moduleId: string) => void
}

interface ModuleCard {
  id: string
  name: string
  icon: string
  description: string
  gradient: string
  iconBg: string
}

const modules: ModuleCard[] = [
  {
    id: 'auth',
    name: 'Autenticación',
    icon: '🔐',
    description: 'Gestión de usuarios y permisos',
    gradient: 'from-blue-500 to-cyan-500',
    iconBg: 'bg-blue-100'
  },
  {
    id: 'inventory',
    name: 'Compras/Inventario',
    icon: '📦',
    description: 'Gestión de compras e inventario',
    gradient: 'from-emerald-500 to-teal-500',
    iconBg: 'bg-emerald-100'
  },
  {
    id: 'clientes',
    name: 'Clientes',
    icon: '👥',
    description: 'Gestión de clientes',
    gradient: 'from-purple-500 to-pink-500',
    iconBg: 'bg-purple-100'
  },
  {
    id: 'proveedores',
    name: 'Proveedores',
    icon: '🏢',
    description: 'Gestión de proveedores',
    gradient: 'from-orange-500 to-red-500',
    iconBg: 'bg-orange-100'
  },
  {
    id: 'unidades',
    name: 'Unidades',
    icon: '🚗',
    description: 'Gestión de unidades vehiculares',
    gradient: 'from-indigo-500 to-purple-500',
    iconBg: 'bg-indigo-100'
  },
  {
    id: 'services',
    name: 'Servicios',
    icon: '⚙️',
    description: 'Gestión de servicios técnicos',
    gradient: 'from-gray-600 to-gray-800',
    iconBg: 'bg-gray-100'
  },
  {
    id: 'sales',
    name: 'Ventas',
    icon: '💰',
    description: 'Módulo de ventas',
    gradient: 'from-green-500 to-emerald-600',
    iconBg: 'bg-green-100'
  },
  {
    id: 'reports',
    name: 'Reportes',
    icon: '📈',
    description: 'Reportes y análisis',
    gradient: 'from-rose-500 to-pink-600',
    iconBg: 'bg-rose-100'
  }
]

export const GeneralDashboard: React.FC<GeneralDashboardProps> = ({ onModuleSelect }) => {
  const handleModuleClick = (moduleId: string) => {
    onModuleSelect?.(moduleId)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">


      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900">
        <div className="absolute inset-0 bg-black/20"></div>
        <div className="relative px-6 py-16 sm:px-8 lg:px-12">
          <div className="mx-auto max-w-7xl">
            <div className="text-center">
              <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl lg:text-7xl">
                <span className="bg-gradient-to-r from-blue-400 to-cyan-300 bg-clip-text text-transparent">
                  Sistema de Gestión
                </span>
                <span className="text-white"> e Inventario</span>
              </h1>
              <p className="mt-6 text-lg leading-8 text-blue-100 dark:text-blue-200 sm:text-xl">
                Sistema integral de gestión vehicular y logística empresarial
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Vehicle Images Section */}
      <div className="relative py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Gestión Integral de Flota
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              Administra todos los aspectos de tu flota vehicular desde una sola plataforma
            </p>
          </div>
          
          {/* Vehicle SVG Icons */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            {/* Bus SVG */}
            <div className="flex flex-col items-center group">
              <div className="relative p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-xl dark:hover:shadow-2xl transition-all duration-300 group-hover:scale-105">
                <svg className="w-24 h-24 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4s-8 .5-8 4v10zm3.5 1c-.83 0-1.5-.67-1.5-1.5S6.67 14 7.5 14s1.5.67 1.5 1.5S8.33 17 7.5 17zm9 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm1.5-6H6V6h12v5z"/>
                </svg>
              </div>
              <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">Autobuses</h3>
              <p className="text-gray-600 dark:text-gray-300">Transporte público y privado</p>
            </div>

            {/* Truck SVG */}
            <div className="flex flex-col items-center group">
              <div className="relative p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-xl dark:hover:shadow-2xl transition-all duration-300 group-hover:scale-105">
                <svg className="w-24 h-24 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 8h-3V4H3c-1.1 0-2 .9-2 2v11h2c0 1.66 1.34 3 3 3s3-1.34 3-3h6c0 1.66 1.34 3 3 3s3-1.34 3-3h2v-5l-3-4zM6 18.5c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zm13.5-9l1.96 2.5H17V9.5h2.5zm-1.5 9c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5z"/>
                </svg>
              </div>
              <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">Camiones</h3>
              <p className="text-gray-600 dark:text-gray-300">Carga y logística</p>
            </div>

            {/* Car SVG */}
            <div className="flex flex-col items-center group">
              <div className="relative p-8 bg-white dark:bg-gray-800 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 group-hover:scale-105">
                <svg className="w-24 h-24 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
                </svg>
              </div>
              <h3 className="mt-4 text-xl font-semibold text-gray-900 dark:text-white">Automóviles</h3>
              <p className="text-gray-600 dark:text-gray-300">Vehículos ejecutivos</p>
            </div>
          </div>
        </div>
      </div>

      {/* Modules Grid */}
      <div className="py-16 bg-white/50 dark:bg-gray-900/50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
              Módulos del Sistema
            </h2>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
              Accede a todas las funcionalidades desde un solo lugar
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 lg:gap-8">
            {modules.map((module) => (
              <div
                key={module.id}
                onClick={() => handleModuleClick(module.id)}
                className="group relative cursor-pointer"
              >
                <div className="relative overflow-hidden rounded-2xl bg-white dark:bg-gray-800 p-6 shadow-lg transition-all duration-300 hover:shadow-2xl hover:-translate-y-2">
                  {/* Gradient Background */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${module.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-10`}></div>
                  
                  {/* Icon Container */}
                  <div className={`relative mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-xl ${module.iconBg} transition-all duration-300 group-hover:scale-110`}>
                    <span className="text-2xl">{module.icon}</span>
                  </div>
                  
                  {/* Module Name */}
                  <h3 className="relative text-center text-sm font-semibold text-gray-900 dark:text-white group-hover:text-gray-800 dark:group-hover:text-gray-200">
                    {module.name}
                  </h3>
                  
                  {/* Description (hidden on mobile, shown on hover) */}
                  <p className="relative mt-2 text-center text-xs text-gray-600 dark:text-gray-400 opacity-0 transition-opacity duration-300 group-hover:opacity-100 hidden md:block">
                    {module.description}
                  </p>
                  
                  {/* Hover Effect Border */}
                  <div className={`absolute inset-0 rounded-2xl border-2 border-transparent bg-gradient-to-br ${module.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-100`}
                       style={{ padding: '2px' }}>
                    <div className="h-full w-full rounded-xl bg-white"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gradient-to-r from-slate-900 to-blue-900 py-12">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="text-center">
            <p className="text-blue-200 dark:text-gray-300">
              © 2024 Fleet Management System. Tecnología avanzada para la gestión vehicular.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}