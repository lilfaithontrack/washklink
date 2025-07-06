import React, { useState, useEffect } from 'react'
import { Search, Plus, MapPin, Star, Phone, Mail } from 'lucide-react'
import { providerService } from '../services/api'
import toast from 'react-hot-toast'

interface Provider {
  id: number
  first_name: string
  middle_name: string
  last_name: string
  email: string
  phone_number: string
  address: string
  nearby_condominum: string
  latitude: number
  longitude: number
  washing_machine: boolean
  date_of_birth: string
  is_active?: boolean
  rating?: number
  total_orders_completed?: number
}

const Providers: React.FC = () => {
  const [providers, setProviders] = useState<Provider[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchProviders()
  }, [])

  const fetchProviders = async () => {
    try {
      setLoading(true)
      const response = await providerService.getProviders()
      setProviders(response.data)
    } catch (error) {
      toast.error('Failed to fetch providers')
      console.error('Error fetching providers:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredProviders = providers.filter(provider => {
    const fullName = `${provider.first_name} ${provider.middle_name} ${provider.last_name}`
    return fullName.toLowerCase().includes(searchTerm.toLowerCase()) ||
           provider.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
           provider.address.toLowerCase().includes(searchTerm.toLowerCase())
  })

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
          <h1 className="text-2xl font-bold text-gray-900">Service Providers</h1>
          <p className="text-gray-600">Manage laundry service providers</p>
        </div>
        <button className="btn btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Add Provider
        </button>
      </div>

      {/* Search */}
      <div className="card">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search providers..."
            className="input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {/* Providers Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProviders.map((provider) => (
          <div key={provider.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center">
                <div className="h-12 w-12 rounded-full bg-primary-600 flex items-center justify-center">
                  <span className="text-lg font-medium text-white">
                    {provider.first_name.charAt(0)}
                  </span>
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-medium text-gray-900">
                    {`${provider.first_name} ${provider.middle_name} ${provider.last_name}`}
                  </h3>
                  <div className="flex items-center">
                    <Star className="h-4 w-4 text-yellow-400 fill-current" />
                    <span className="ml-1 text-sm text-gray-600">
                      {provider.rating?.toFixed(1) || '4.5'}
                    </span>
                  </div>
                </div>
              </div>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                provider.is_active !== false ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {provider.is_active !== false ? 'Active' : 'Inactive'}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center text-sm text-gray-600">
                <Mail className="h-4 w-4 mr-2" />
                {provider.email}
              </div>
              <div className="flex items-center text-sm text-gray-600">
                <Phone className="h-4 w-4 mr-2" />
                {provider.phone_number}
              </div>
              <div className="flex items-start text-sm text-gray-600">
                <MapPin className="h-4 w-4 mr-2 mt-0.5" />
                <div>
                  <div>{provider.address}</div>
                  <div className="text-xs text-gray-500">Near {provider.nearby_condominum}</div>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Orders Completed:</span>
                <span className="font-medium">{provider.total_orders_completed || 0}</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-gray-600">Has Washing Machine:</span>
                <span className={`font-medium ${provider.washing_machine ? 'text-green-600' : 'text-red-600'}`}>
                  {provider.washing_machine ? 'Yes' : 'No'}
                </span>
              </div>
            </div>

            <div className="mt-4 flex space-x-2">
              <button className="flex-1 btn btn-secondary text-sm">
                View Details
              </button>
              <button className="flex-1 btn btn-primary text-sm">
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredProviders.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-500">
            {searchTerm ? 'No providers found matching your search.' : 'No providers found.'}
          </div>
        </div>
      )}
    </div>
  )
}

export default Providers