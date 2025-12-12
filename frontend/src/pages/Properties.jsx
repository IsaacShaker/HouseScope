import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function Properties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState('');
  const [scrapeResult, setScrapeResult] = useState(null);
  
  // Search filters
  const [filters, setFilters] = useState({
    city: 'Pittsburgh',
    state: 'PA',
    max_price: 500000,
    min_beds: 2,
    min_baths: 1,
    property_type: ''
  });

  useEffect(() => {
    fetchProperties();
  }, []);

  const fetchProperties = async () => {
    try {
      setLoading(true);
      setError('');
      const token = localStorage.getItem('token');
      
      const params = new URLSearchParams();
      if (filters.city) params.append('city', filters.city);
      if (filters.state) params.append('state', filters.state);
      if (filters.max_price) params.append('max_price', filters.max_price);
      if (filters.min_beds) params.append('min_beds', filters.min_beds);
      if (filters.min_baths) params.append('min_baths', filters.min_baths);
      if (filters.property_type) params.append('property_type', filters.property_type);
      params.append('limit', '50');
      
      const response = await axios.get(`${API_URL}/api/properties?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setProperties(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch properties');
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async () => {
    try {
      setScraping(true);
      setError('');
      setScrapeResult(null);
      const token = localStorage.getItem('token');
      
      const response = await axios.post(
        `${API_URL}/api/properties/scrape`,
        {
          city: filters.city,
          state: filters.state,
          sources: ['redfin'],
          max_price: filters.max_price ? parseInt(filters.max_price) : null,
          min_beds: filters.min_beds ? parseInt(filters.min_beds) : null,
          min_baths: filters.min_baths ? parseFloat(filters.min_baths) : null,
          property_type: filters.property_type || null
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      setScrapeResult(response.data);
      
      // Refresh properties list after scraping
      setTimeout(() => {
        fetchProperties();
      }, 1000);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to scrape properties');
    } finally {
      setScraping(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Property Search</h1>
        <p className="text-gray-600">Search and scrape real estate listings</p>
      </div>

      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Search Filters</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              City
            </label>
            <input
              type="text"
              value={filters.city}
              onChange={(e) => setFilters({ ...filters, city: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Pittsburgh"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <input
              type="text"
              value={filters.state}
              onChange={(e) => setFilters({ ...filters, state: e.target.value.toUpperCase() })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="PA"
              maxLength="2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Price
            </label>
            <input
              type="number"
              value={filters.max_price}
              onChange={(e) => setFilters({ ...filters, max_price: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="500000"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Beds
            </label>
            <input
              type="number"
              value={filters.min_beds}
              onChange={(e) => setFilters({ ...filters, min_beds: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Min Baths
            </label>
            <input
              type="number"
              step="0.5"
              value={filters.min_baths}
              onChange={(e) => setFilters({ ...filters, min_baths: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              min="0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Property Type
            </label>
            <select
              value={filters.property_type}
              onChange={(e) => setFilters({ ...filters, property_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Types</option>
              <option value="house">House</option>
              <option value="condo">Condo</option>
              <option value="townhouse">Townhouse</option>
            </select>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={handleScrape}
            disabled={scraping || !filters.city || !filters.state}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {scraping ? 'Scraping...' : '🔍 Scrape Redfin'}
          </button>
          
          <button
            onClick={fetchProperties}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Loading...' : '🔄 Refresh Results'}
          </button>
        </div>
      </div>

      {/* Scrape Results */}
      {scrapeResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-green-800 mb-2">✅ Scraping Complete</h3>
          <p className="text-green-700 mb-2">{scrapeResult.message}</p>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Found:</span> {scrapeResult.total_found} properties
            </div>
            <div>
              <span className="font-medium">Saved:</span> {scrapeResult.total_saved} new properties
            </div>
          </div>
          {scrapeResult.by_source && (
            <div className="mt-2 text-sm">
              {Object.entries(scrapeResult.by_source).map(([source, data]) => (
                <div key={source} className="text-green-600">
                  <span className="font-medium capitalize">{source}:</span> Found {data.found}, Saved {data.saved}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-700">{error}</p>
        </div>
      )}

      {/* Properties Grid */}
      <div className="mb-4">
        <h2 className="text-2xl font-semibold text-gray-900">
          {properties.length} Properties Found
        </h2>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading properties...</p>
        </div>
      ) : properties.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-12 text-center">
          <p className="text-gray-600 text-lg">No properties found. Try scraping some listings!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {properties.map((property) => (
            <div
              key={property.id}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow"
            >
              {/* Property Image Placeholder */}
              <div className="h-48 bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                <span className="text-6xl">🏠</span>
              </div>

              {/* Property Details */}
              <div className="p-5">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-2xl font-bold text-blue-600">
                    {formatPrice(property.price)}
                  </h3>
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded uppercase">
                    {property.source}
                  </span>
                </div>

                <p className="text-gray-700 font-medium mb-1">{property.address}</p>
                <p className="text-gray-500 text-sm mb-3">
                  {property.city}, {property.state} {property.zip_code}
                </p>

                <div className="flex gap-4 text-sm text-gray-600 mb-3">
                  <div className="flex items-center gap-1">
                    <span className="font-semibold">{property.beds}</span>
                    <span>beds</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-semibold">{property.baths}</span>
                    <span>baths</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="font-semibold">{property.sqft.toLocaleString()}</span>
                    <span>sqft</span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                  <span className="capitalize">{property.property_type}</span>
                  {property.year_built && <span>Built {property.year_built}</span>}
                </div>

                {property.listing_url && (
                  <a
                    href={property.listing_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                  >
                    View on Redfin →
                  </a>
                )}

                {/* Scores (if available) */}
                {(property.homebuyer_score || property.investor_score) && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex gap-3 text-xs">
                      {property.homebuyer_score && (
                        <div>
                          <span className="text-gray-600">Homebuyer: </span>
                          <span className="font-semibold">{property.homebuyer_score}/100</span>
                        </div>
                      )}
                      {property.investor_score && (
                        <div>
                          <span className="text-gray-600">Investor: </span>
                          <span className="font-semibold">{property.investor_score}/100</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Properties;
