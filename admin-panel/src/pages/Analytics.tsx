import React, { useState, useEffect } from 'react'
import { TrendingUp, Users, ShoppingBag, DollarSign, Clock, MapPin } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { analyticsService } from '../services/api'

const Analytics: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState('7d')

  // Sample data for charts
  const revenueData = [
    { date: '2024-01-01', revenue: 4000, orders: 24, users: 12 },
    { date: '2024-01-02', revenue: 3000, orders: 18, users: 8 },
    { date: '2024-01-03', revenue: 5000, orders: 30, users: 15 },
    { date: '2024-01-04', revenue: 4500, orders: 27, users: 13 },
    { date: '2024-01-05', revenue: 6000, orders: 35, users: 18 },
    { date: '2024-01-06', revenue: 5500, orders: 32, users: 16 },
    { date: '2024-01-07', revenue: 7000, orders: 40, users: 20 },
  ]

  const orderStatusData = [
    { name: 'Completed', value: 65, color: '#10B981' },
    { name: 'In Progress', value: 20, color: '#F59E0B' },
    { name: 'Pending', value: 10, color: '#EF4444' },
    { name: 'Cancelled', value: 5, color: '#6B7280' },
  ]

  const serviceTypeData = [
    { name: 'Machine Wash', orders: 120, revenue: 18000 },
    { name: 'Hand Wash', orders: 80, revenue: 16000 },
    { name: 'Premium Service', orders: 40, revenue: 12000 },
    { name: 'Dry Cleaning', orders: 30, revenue: 9000 },
  ]

  const hourlyData = [
    { hour: '6AM', orders: 2 },
    { hour: '8AM', orders: 8 },
    { hour: '10AM', orders: 15 },
    { hour: '12PM', orders: 25 },
    { hour: '2PM', orders: 20 },
    { hour: '4PM', orders: 18 },
    { hour: '6PM', orders: 22 },
    { hour: '8PM', orders: 12 },
    { hour: '10PM', orders: 5 },
  ]

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true)
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
      } catch (error) {
        console.error('Error fetching analytics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalytics()
  }, [timeRange])

  const kpiCards = [
    {
      title: 'Total Revenue',
      value: 'ETB 125,000',
      change: '+15.3%',
      changeType: 'positive',
      icon: DollarSign,
      color: 'bg-green-500'
    },
    {
      title: 'Total Orders',
      value: '1,234',
      change: '+8.2%',
      changeType: 'positive',
      icon: ShoppingBag,
      color: 'bg-blue-500'
    },
    {
      title: 'Active Users',
      value: '856',
      change: '+12.1%',
      changeType: 'positive',
      icon: Users,
      color: 'bg-purple-500'
    },
    {
      title: 'Avg. Order Time',
      value: '2.5 hrs',
      change: '-5.4%',
      changeType: 'positive',
      icon: Clock,
      color: 'bg-orange-500'
    }
  ]

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
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Comprehensive business insights and metrics</p>
        </div>
        <select
          className="input w-auto"
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
        >
          <option value="7d">Last 7 days</option>
          <option value="30d">Last 30 days</option>
          <option value="90d">Last 90 days</option>
          <option value="1y">Last year</option>
        </select>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((kpi, index) => {
          const Icon = kpi.icon
          return (
            <div key={index} className="card">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${kpi.color}`}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{kpi.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{kpi.value}</p>
                  <p className={`text-sm ${kpi.changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
                    {kpi.change} from last period
                  </p>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Revenue and Orders Chart */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue & Orders Trend</h3>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={revenueData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString()} />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleDateString()}
              formatter={(value, name) => [
                name === 'revenue' ? `ETB ${value}` : value,
                name === 'revenue' ? 'Revenue' : 'Orders'
              ]}
            />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="revenue"
              stackId="1"
              stroke="#3B82F6"
              fill="#3B82F6"
              fillOpacity={0.3}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="orders"
              stroke="#10B981"
              strokeWidth={3}
              dot={{ fill: '#10B981' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Order Status Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={orderStatusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {orderStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Service Types Performance */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Service Types Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={serviceTypeData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="orders" fill="#3B82F6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Hourly Orders Pattern */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Hourly Order Pattern</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={hourlyData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Area
              type="monotone"
              dataKey="orders"
              stroke="#8B5CF6"
              fill="#8B5CF6"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h4 className="font-medium text-gray-900 mb-4">Top Performing Providers</h4>
          <div className="space-y-3">
            {[
              { name: 'Ahmed Hassan', orders: 45, rating: 4.9 },
              { name: 'Fatima Ali', orders: 38, rating: 4.8 },
              { name: 'Mohammed Said', orders: 32, rating: 4.7 },
            ].map((provider, index) => (
              <div key={index} className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-sm">{provider.name}</div>
                  <div className="text-xs text-gray-500">{provider.orders} orders</div>
                </div>
                <div className="text-sm font-medium text-yellow-600">
                  ⭐ {provider.rating}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h4 className="font-medium text-gray-900 mb-4">Popular Service Areas</h4>
          <div className="space-y-3">
            {[
              { area: 'Bole', orders: 156, percentage: 35 },
              { area: 'Kirkos', orders: 124, percentage: 28 },
              { area: 'Yeka', orders: 98, percentage: 22 },
              { area: 'Addis Ketema', orders: 67, percentage: 15 },
            ].map((area, index) => (
              <div key={index} className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>{area.area}</span>
                  <span>{area.orders} orders</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${area.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h4 className="font-medium text-gray-900 mb-4">Customer Satisfaction</h4>
          <div className="space-y-4">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">4.8</div>
              <div className="text-sm text-gray-600">Average Rating</div>
            </div>
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((stars) => (
                <div key={stars} className="flex items-center space-x-2">
                  <span className="text-sm w-8">{stars}★</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-yellow-400 h-2 rounded-full"
                      style={{ width: `${stars === 5 ? 70 : stars === 4 ? 20 : stars === 3 ? 7 : stars === 2 ? 2 : 1}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600 w-8">
                    {stars === 5 ? '70%' : stars === 4 ? '20%' : stars === 3 ? '7%' : stars === 2 ? '2%' : '1%'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Analytics