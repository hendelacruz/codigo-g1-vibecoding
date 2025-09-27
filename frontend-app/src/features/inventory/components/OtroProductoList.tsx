import React, { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { 
  FiEdit2, 
  FiTrash2, 
  FiEye, 
  FiPlus,
  FiPackage,
  FiAlertTriangle,
  FiLoader
} from 'react-icons/fi'
import type { OtroProducto } from '../inventoryTypes'
import { useInventory } from '../hooks/useInventory'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'
import { Select } from '../../../shared/components/ui/Select'
import { Badge } from '../../../shared/components/ui/Badge'
import { Card, CardContent, CardHeader, CardTitle } from '../../../shared/components/ui/Card'
import { formatPrice } from '../../../shared/lib/utils'

interface OtroProductoListProps {
  onEdit?: (producto: OtroProducto) => void
  onAdd?: () => void
}



export const OtroProductoList: React.FC<OtroProductoListProps> = ({ onEdit, onAdd }) => {
  const { 
    otrosProductos, 
    removeOtroProducto, 
    loadOtrosProductos,
    adjustProductStock
  } = useInventory()

  // Load products when component mounts
  useEffect(() => {
    loadOtrosProductos()
  }, [loadOtrosProductos])

  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [stockFilter, setStockFilter] = useState('all')
  const [selectedProduct, setSelectedProduct] = useState<OtroProducto | null>(null)
  const [showDetails, setShowDetails] = useState(false)
  const [showStockModal, setShowStockModal] = useState(false)
  const [stockAdjustment, setStockAdjustment] = useState({ cantidad: 0, motivo: '' })
  const [deletingProducts, setDeletingProducts] = useState<Set<number>>(new Set())

  // Filter products based on search term, category, and stock status
  const filteredProducts = useMemo(() => {
    const items = Array.isArray(otrosProductos?.items) ? otrosProductos.items : []
    let filtered = [...items]
    
    if (searchTerm) {
      const term = searchTerm.toLowerCase()
      filtered = filtered.filter(product => 
        product.nombre.toLowerCase().includes(term) ||
        (product.descripcion || '').toLowerCase().includes(term) ||
        product.categoria.toLowerCase().includes(term) ||
        product.id.toString().includes(term)
      )
    }

    if (categoryFilter !== 'all') {
      filtered = filtered.filter(product => product.categoria === categoryFilter)
    }

    if (stockFilter !== 'all') {
      filtered = filtered.filter(product => {
        switch (stockFilter) {
          case 'bajo_stock':
            return product.stock_actual <= product.stock_minimo
          case 'sin_stock':
            return product.stock_actual === 0
          case 'con_stock':
            return product.stock_actual > product.stock_minimo
          default:
            return true
        }
      })
    }

    return filtered
  }, [otrosProductos?.items, searchTerm, categoryFilter, stockFilter])

  // Get unique categories from products
  const availableCategories = useMemo(() => {
    const items = Array.isArray(otrosProductos?.items) ? otrosProductos.items : []
    return Array.from(new Set(items.map(product => product.categoria)))
  }, [otrosProductos?.items])

  const handleDelete = async (id: number) => {
    const product = otrosProductos?.items?.find(p => p.id === id)
    if (!product) return

    const confirmMessage = `¿Está seguro de que desea eliminar el producto "${product.nombre}"?`
    
    if (window.confirm(confirmMessage)) {
      // Prevent multiple simultaneous deletes on the same product
      if (deletingProducts.has(id)) {
        toast.error('Operación en progreso, por favor espere...')
        return
      }

      // Add product to deleting set
      setDeletingProducts(prev => new Set(prev).add(id))

      try {
        await removeOtroProducto(id)
        toast.success(`Producto "${product.nombre}" eliminado exitosamente`)
        // Reload the list after deletion
        loadOtrosProductos()
      } catch (error) {
        console.error('Error al eliminar producto:', error)
        toast.error('Error al eliminar el producto. Por favor, intente nuevamente.')
      } finally {
        // Remove product from deleting set
        setDeletingProducts(prev => {
          const newSet = new Set(prev)
          newSet.delete(id)
          return newSet
        })
      }
    }
  }

  const handleStockAdjustment = async () => {
    if (!selectedProduct) return

    if (stockAdjustment.cantidad === 0) {
      toast.error('La cantidad debe ser diferente de 0')
      return
    }

    try {
      await adjustProductStock(selectedProduct.id, { cantidad: stockAdjustment.cantidad, motivo: stockAdjustment.motivo })
      toast.success(`Stock ajustado exitosamente para "${selectedProduct.nombre}"`)
      
      // Reset stock adjustment form
      setStockAdjustment({ cantidad: 0, motivo: '' })
      setShowStockModal(false)
      setSelectedProduct(null)
      
      // Reload products
      loadOtrosProductos()
    } catch (error) {
      console.error('Error al ajustar stock:', error)
      toast.error('Error al ajustar el stock. Por favor, intente nuevamente.')
    }
  }

  const handleViewDetails = (product: OtroProducto) => {
    setSelectedProduct(product)
    setShowDetails(true)
  }

  const handleOpenStockModal = (product: OtroProducto) => {
    setSelectedProduct(product)
    setShowStockModal(true)
    setStockAdjustment({ cantidad: 0, motivo: '' })
  }

  const getStockBadgeVariant = (product: OtroProducto) => {
    if (product.stock_actual === 0) return 'error'
    if (product.stock_actual <= product.stock_minimo) return 'warning'
    return 'success'
  }

  const getStockStatusText = (product: OtroProducto) => {
    if (product.stock_actual === 0) return 'Sin Stock'
    if (product.stock_actual <= product.stock_minimo) return 'Stock Bajo'
    return 'Stock OK'
  }

  if (otrosProductos.isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    )
  }

  if (otrosProductos.error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 mb-4">Error al cargar los productos</div>
        <Button onClick={() => loadOtrosProductos()}>
          Reintentar
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header with Add Button */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Otros Productos</h2>
        <Button onClick={onAdd} className="flex items-center gap-2">
          <FiPlus className="w-4 h-4" />
          Agregar Producto
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                Buscar
              </label>
              <Input
                id="search"
                type="text"
                placeholder="Nombre, descripción, ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                Categoría
              </label>
              <Select
                id="category"
                value={categoryFilter}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setCategoryFilter(e.target.value)}
              >
                <option value="all">Todas las categorías</option>
                {availableCategories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </Select>
            </div>

            {/* Stock Filter */}
            <div>
              <label htmlFor="stock" className="block text-sm font-medium text-gray-700 mb-1">
                Estado de Stock
              </label>
              <Select
                id="stock"
                value={stockFilter}
                onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setStockFilter(e.target.value)}
              >
                <option value="all">Todos</option>
                <option value="con_stock">Con Stock</option>
                <option value="bajo_stock">Stock Bajo</option>
                <option value="sin_stock">Sin Stock</option>
              </Select>
            </div>

            {/* Results Count */}
            <div className="flex items-end">
              <div className="text-sm text-gray-600">
                {filteredProducts.length} producto{filteredProducts.length !== 1 ? 's' : ''} encontrado{filteredProducts.length !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Products Grid */}
      {filteredProducts.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <FiPackage className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No se encontraron productos</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || categoryFilter !== 'all' || stockFilter !== 'all'
                ? 'Intenta ajustar los filtros para ver más resultados.'
                : 'Comienza agregando tu primer producto.'}
            </p>
            {(!searchTerm && categoryFilter === 'all' && stockFilter === 'all') && (
              <Button onClick={onAdd}>
                Agregar Primer Producto
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <Card key={product.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg">{product.nombre}</CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{product.categoria}</p>
                  </div>
                  <Badge variant={getStockBadgeVariant(product)}>
                    {getStockStatusText(product)}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                {/* Description */}
                {product.descripcion && (
                  <p 
                    className="text-sm text-gray-600 mb-3 overflow-hidden"
                    style={{
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      wordBreak: 'break-word',
                      hyphens: 'auto'
                    }}
                  >
                    {product.descripcion}
                  </p>
                )}

                {/* Stock and Price Info */}
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Stock Actual:</span>
                    <span className="font-medium">{product.stock_actual}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Stock Mínimo:</span>
                    <span className="font-medium">{product.stock_minimo}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Precio Unitario:</span>
                    <span className="font-medium">S/ {formatPrice(product.precio_unitario, 2)}</span>
                  </div>
                </div>

                {/* Stock Warning */}
                {product.stock_actual <= product.stock_minimo && (
                  <div className="flex items-center gap-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md mb-4">
                    <FiAlertTriangle className="w-4 h-4 text-yellow-600" />
                    <span className="text-sm text-yellow-800">
                      {product.stock_actual === 0 ? 'Sin stock disponible' : 'Stock bajo'}
                    </span>
                  </div>
                )}

                {/* Actions */}
                <div className="flex justify-between items-center">
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewDetails(product)}
                      title="Ver detalles"
                    >
                      <FiEye className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onEdit?.(product)}
                      title="Editar producto"
                    >
                      <FiEdit2 className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(product.id)}
                      disabled={deletingProducts.has(product.id)}
                      title="Eliminar producto"
                    >
                      {deletingProducts.has(product.id) ? (
                        <FiLoader className="w-4 h-4 animate-spin" />
                      ) : (
                        <FiTrash2 className="w-4 h-4 text-red-600" />
                      )}
                    </Button>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleOpenStockModal(product)}
                    title="Ajustar stock"
                  >
                    Ajustar Stock
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Product Details Modal */}
      {showDetails && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Detalles del Producto</h3>
              <Button
                variant="ghost"
                onClick={() => setShowDetails(false)}
              >
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                <p className="text-gray-900">{selectedProduct.nombre}</p>
              </div>
              
              {selectedProduct.descripcion && (
                <div>
                  <label className="block text-sm font-medium text-gray-700">Descripción</label>
                  <p className="text-gray-900">{selectedProduct.descripcion}</p>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Categoría</label>
                  <p className="text-gray-900">{selectedProduct.categoria}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Precio Unitario</label>
                  <p className="text-gray-900">${formatPrice(selectedProduct.precio_unitario, 2)}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Stock Actual</label>
                  <p className="text-gray-900">{selectedProduct.stock_actual}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Stock Mínimo</label>
                  <p className="text-gray-900">{selectedProduct.stock_minimo}</p>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700">Estado de Stock</label>
                <Badge variant={getStockBadgeVariant(selectedProduct)}>
                  {getStockStatusText(selectedProduct)}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stock Adjustment Modal */}
      {showStockModal && selectedProduct && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Ajustar Stock</h3>
              <Button
                variant="ghost"
                onClick={() => setShowStockModal(false)}
              >
                ✕
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Producto: <strong>{selectedProduct.nombre}</strong></p>
                <p className="text-sm text-gray-600">Stock actual: <strong>{selectedProduct.stock_actual}</strong></p>
              </div>
              
              <div>
                <label htmlFor="cantidad" className="block text-sm font-medium text-gray-700 mb-1">
                  Cantidad (+ para agregar, - para quitar)
                </label>
                <Input
                  id="cantidad"
                  type="number"
                  value={stockAdjustment.cantidad}
                  onChange={(e) => setStockAdjustment(prev => ({ 
                    ...prev, 
                    cantidad: parseInt(e.target.value) || 0 
                  }))}
                  placeholder="0"
                />
              </div>
              
              <div>
                <label htmlFor="motivo" className="block text-sm font-medium text-gray-700 mb-1">
                  Motivo (opcional)
                </label>
                <Input
                  id="motivo"
                  type="text"
                  value={stockAdjustment.motivo}
                  onChange={(e) => setStockAdjustment(prev => ({ 
                    ...prev, 
                    motivo: e.target.value 
                  }))}
                  placeholder="Ej: Compra, Venta, Ajuste de inventario..."
                />
              </div>
              
              <div className="flex justify-end gap-2">
                <Button
                  variant="secondary"
                  onClick={() => setShowStockModal(false)}
                >
                  Cancelar
                </Button>
                <Button
                  onClick={handleStockAdjustment}
                  disabled={stockAdjustment.cantidad === 0}
                >
                  Ajustar Stock
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}