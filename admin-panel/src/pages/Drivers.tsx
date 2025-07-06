import React, { useState, useEffect } from 'react'
import { Search, Plus, MapPin, Star, Phone, Car, Clock } from 'lucide-react'
import { driverService } from '../services/api'
import toast from 'react-hot-toast'

interface Driver {
  id: number
  first_name: string
  last_name: string
  email: string
  phone_number: string
  license_number: string
  vehicle_type: string
  vehicle_plate: string
  vehicle_model?: string
  vehicle_color?: string
  status: string
  is_active: boolean
  rating: number
  total_deliveries: number
  successful_deliveries: number
  current_latitude?: number
  current_longitude?: number
  last_active: string
}

const Drivers: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  useEffect(() => {
    fetchDrivers()
  }, [])

  const fetchDrivers = async () => {
    try {
      setLoading(true)
      const response = await driverService.getDrivers()
      setDrivers(response.data)
    } catch (error) {
      toast.error('Failed to fetch drivers')
      console.error('Error fetching drivers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusUpdate = async (driverId: number, newStatus: string) => {
    try {
      await driverService.updateDriverStatus(driverId, newStatus)
      toast.success('Driver status updated successfully')
      fetchDrivers()
    } catch (error) {
      toast.error('Failed to update driver status')
    }
  }

  const filteredDrivers = drivers.filter(driver => {
    const fullName = `${driver.first_name} ${driver.last_name}`
    const matchesSearch = fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         driver.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         driver.vehicle_plate.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === 'all' || driver.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available': return 'bg-green-100 text-green-800'
      case 'busy': return 'bg-yellow-100 text-yellow-800'
      case 'on_delivery': return 'bg-blue-100 text-blue-800'
      case 'offline': return 'bg-gray-100 text-gray-800'
      case 'suspended': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getVehicleIcon = (vehicleType: string) => {
    switch (vehicleType.toLowerCase()) {
      case 'motorcycle': return '🏍️'
      case 'car': return '🚗'
      case 'van': return '🚐'
      case 'bicycle': return '🚲'
      default: return '🚗'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Drivers</h1>
          <p className="text-gray-600">Manage delivery drivers and their status</p>
        </div>
        <button className="btn btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Driver
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search drivers..."
              className="input pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <select
            className="input w-full sm:w-auto"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="available">Available</option>
            <option value="busy">Busy</option>
            <option value="on_delivery">On Delivery</option>
            <option value="offline">Offline</option>
            <option value="suspended">Suspended</option>
          </select>
        </div>
      </div>

      {/* Drivers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDrivers.map((driver) => (
          <div key={driver.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="h-12 w-12 rounded-full bg-primary-600 flex items-center justify-center">
                  <span className="text-lg font-medium text-white">
                    {driver.first_name.charAt(0)}
                  </span>
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-medium text-gray-900">
                    {`${driver.first_name} ${driver.last_name}`}
                  </h3>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="ml-1 text-sm text-gray-600">
                      {driver.rating.toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusBadgeColor(driver.status)}`}>
                {driver.status.replace('_', ' ')}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-sm text-gray-600">
                <Phone className="h-4 w-4 mr-2" />
                {driver.phone_number}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Car className="h-4 w-4 mr-2" />
                <div>
                  <span className="mr-2">{getVehicleIcon(driver.vehicle_type)}</span>
                  {driver.vehicle_plate}
                  {driver.vehicle_model && (
                    <div className="text-xs text-gray-500">
                      {driver.vehicle_color} {driver.vehicle_model}
                    </div>
                  )}
                </div>
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Clock className="h-4 w-4 mr-2" />
                Last active: {new Date(driver.last_active).toLocaleDateString()}
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Total Deliveries:</span>
                  <div className="font-medium">{driver.total_deliveries}</div>
                </div>
                <div>
                  <span className="text-gray-600">Success Rate:</span>
                  <div className="font-medium">
                    {driver.total_deliveries > 0 
                      ? `${((driver.successful_deliveries / driver.total_deliveries) * 100).toFixed(1)}%`
                      : 'N/A'
                    }
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <select
                value={driver.status}
                onChange={(e) => handleStatusUpdate(driver.id, e.target.value)}
                className="w-full text-sm border border-gray-300 rounded px-3 py-2"
              >
                <option value="available">Available</option>
                <option value="busy">Busy</option>
                <option value="on_delivery">On Delivery</option>
                <option value="offline">Offline</option>
                <option value="suspended">Suspended</option>
              </select>
              
              <div className="flex space-x-2">
                <button className="flex-1 btn btn-secondary text-sm">
                  View Details
                </button>
                <button className="flex-1 btn btn-primary text-sm">
                  Edit
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredDrivers.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            {searchTerm ? 'No drivers found matching your search.' : 'No drivers found.'}
          </div>
        </div>
      )}
    </div>
  )
}

export default Drivers