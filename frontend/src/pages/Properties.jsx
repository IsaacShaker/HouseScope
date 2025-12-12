import { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, RefreshCw, Home, CheckCircle, Plus, X, Users } from 'lucide-react';

const API_URL = 'http://localhost:8000';

function Properties() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [error, setError] = useState('');
  const [scrapeResult, setScrapeResult] = useState(null);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [filteringCommute, setFilteringCommute] = useState(false);
  const [roommates, setRoommates] = useState([
    { destination: '', max_commute_minutes: 30, mode: 'driving' }
  ]);
  
  const [filters, setFilters] = useState({
    city: 'Pittsburgh',
    state: 'PA',
    max_price: 500000,
    min_beds: 2,
    min_baths: 1,
    property_type: ''
  });

  useEffect(() => {
    fetchAffordability();
    fetchProperties();
  }, []);

  const fetchAffordability = async () => {
    try {
      const token = localStorage.getItem('token');
      
      const accountsResponse = await axios.get(`${API_URL}/api/accounts`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (!accountsResponse.data || accountsResponse.data.length === 0) {
        return;
      }
      
      const params = new URLSearchParams({
        down_payment_percent: '20',
        interest_rate: '5.8',
        loan_term_years: '30',
        property_tax_rate: '1.2',
        insurance_rate: '0.5',
        hoa_monthly: '0'
      });
      
      const response = await axios.get(`${API_URL}/api/financial/affordability?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const maxAffordable = response.data.max_home_price;
      const maxPriceWithBuffer = Math.round(maxAffordable * 1.0);
      
      setFilters(prev => ({ ...prev, max_price: maxPriceWithBuffer }));
    } catch (err) {
      console.error('Failed to fetch affordability:', err);
    }
  };

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

  const addRoommate = () => {
    setRoommates([...roommates, { destination: '', max_commute_minutes: 30, mode: 'driving' }]);
  };

  const removeRoommate = (index) => {
    if (roommates.length > 1) {
      setRoommates(roommates.filter((_, i) => i !== index));
    }
  };

  const updateRoommate = (index, field, value) => {
    const updated = [...roommates];
    updated[index][field] = value;
    setRoommates(updated);
  };

  const handleCommuteFilter = async () => {
    if (properties.length === 0) {
      setError('Please search for properties first before filtering by commute');
      return;
    }

    const validRoommates = roommates.filter(rm => rm.destination.trim());
    if (validRoommates.length === 0) {
      setError('Please enter at least one destination address');
      return;
    }

    try {
      setFilteringCommute(true);
      setError('');
      const token = localStorage.getItem('token');

      const propertyIds = properties.map(p => p.id);

      const response = await axios.post(
        `${API_URL}/api/properties/filter-by-commute`,
        {
          property_ids: propertyIds,
          roommates: validRoommates
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const compatibleIds = response.data.compatible_properties.map(p => p.property_id);
      const filtered = properties.filter(p => compatibleIds.includes(p.id));
      
      filtered.forEach(prop => {
        const commuteData = response.data.compatible_properties.find(cp => cp.property_id === prop.id);
        if (commuteData) {
          prop.commute_details = commuteData.commute_details;
        }
      });

      setProperties(filtered);
      setScrapeResult({
        message: response.data.message,
        total_found: response.data.total_checked,
        total_saved: response.data.total_compatible
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to filter properties by commute');
    } finally {
      setFilteringCommute(false);
    }
  };

  return (
    <>
      {/* Page Header */}
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
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
          >
            <Search className="h-4 w-4" />
            {scraping ? 'Scraping...' : 'Scrape Redfin'}
          </button>
          
          <button
            onClick={fetchProperties}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            {loading ? 'Loading...' : 'Refresh Results'}
          </button>
        </div>
      </div>

      {/* Advanced Search - Commute Filter */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-purple-600" />
            <h2 className="text-xl font-semibold">Advanced Search: Commute Filter</h2>
          </div>
          <button
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-sm text-purple-600 hover:text-purple-700 font-medium"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Search
          </button>
        </div>

        {showAdvanced && (
          <>
            <p className="text-gray-600 text-sm mb-4">
              Filter properties by commute time for multiple roommates. Each roommate can specify their work/school location and maximum acceptable commute time.
            </p>

            <div className="space-y-4 mb-4">
              {roommates.map((roommate, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-medium text-gray-900">Roommate {index + 1}</h3>
                    {roommates.length > 1 && (
                      <button
                        onClick={() => removeRoommate(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="md:col-span-1">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Work/School Address
                      </label>
                      <input
                        type="text"
                        value={roommate.destination}
                        onChange={(e) => updateRoommate(index, 'destination', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        placeholder="123 Main St, Pittsburgh, PA"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Commute (minutes)
                      </label>
                      <input
                        type="number"
                        value={roommate.max_commute_minutes}
                        onChange={(e) => updateRoommate(index, 'max_commute_minutes', parseFloat(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                        min="5"
                        max="180"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Transportation Mode
                      </label>
                      <select
                        value={roommate.mode}
                        onChange={(e) => updateRoommate(index, 'mode', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                      >
                        <option value="driving">Driving</option>
                        <option value="transit">Public Transit</option>
                        <option value="walking">Walking</option>
                        <option value="bicycling">Bicycling</option>
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={addRoommate}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium flex items-center gap-2"
              >
                <Plus className="h-4 w-4" />
                Add Roommate
              </button>

              <button
                onClick={handleCommuteFilter}
                disabled={filteringCommute || properties.length === 0}
                className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
              >
                <Search className="h-4 w-4" />
                {filteringCommute ? 'Filtering...' : 'Filter by Commute'}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Scrape Results */}
      {scrapeResult && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-semibold text-green-800">Scraping Complete</h3>
          </div>
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
              {/* Property Image */}
              <div className="h-48 bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center overflow-hidden">
                {property.image_url ? (
                  <img 
                    src={property.image_url} 
                    alt={property.address}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <Home className="h-20 w-20 text-white opacity-80" />
                )}
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

                {/* Commute Details (if available) */}
                {property.commute_details && property.commute_details.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <h4 className="text-xs font-semibold text-gray-700 mb-2">Commute Times:</h4>
                    <div className="space-y-1">
                      {property.commute_details.map((commute, idx) => (
                        <div key={idx} className="flex items-center justify-between text-xs">
                          <span className="text-gray-600">
                            Roommate {commute.roommate_index} ({commute.mode}):
                          </span>
                          <span className={`font-semibold ${commute.compatible ? 'text-green-600' : 'text-red-600'}`}>
                            {commute.duration_text}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

export default Properties;
