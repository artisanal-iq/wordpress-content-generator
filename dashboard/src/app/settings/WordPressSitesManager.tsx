import { useState, useEffect } from 'react';
import { 
  FiPlus, 
  FiEdit2, 
  FiTrash2, 
  FiCheck, 
  FiX, 
  FiRefreshCw, 
  FiAlertCircle,
  FiGlobe,
  FiSave,
  FiZap
  FiLink
} from 'react-icons/fi';
import supabase from '@/lib/supabase';
import { v4 as uuidv4 } from 'uuid';
import toast from 'react-hot-toast';

// Define types for WordPress sites
type WordPressSite = {
  id: string;
  domain: string;
  url: string;
  username: string;
  app_password: string;
  created_at: string;
  updated_at: string | null;
  scaffold_status?: string;
};

// Form data type
type SiteFormData = {
  domain: string;
  url: string;
  username: string;
  app_password: string;
};

// Empty form initial state
const emptyForm: SiteFormData = {
  domain: '',
  url: '',
  username: '',
  app_password: ''
};

export default function WordPressSitesManager() {
  // State for WordPress sites
  const [sites, setSites] = useState<WordPressSite[]>([]);
  
  // Form state
  const [formData, setFormData] = useState<SiteFormData>(emptyForm);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  // UI state
  const [loading, setLoading] = useState(true);
  const [formLoading, setFormLoading] = useState(false);
  const [testingConnection, setTestingConnection] = useState<string | null>(null);
  const [bootstrappingSite, setBootstrappingSite] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Fetch WordPress sites on component mount
  useEffect(() => {
    fetchWordPressSites();
  }, []);
  
  // Fetch WordPress sites from database
  const fetchWordPressSites = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const { data, error } = await supabase
        .from('wordpress_sites')
        .select('*')
        .order('domain', { ascending: true });
      
      if (error) throw new Error(error.message);
      
      setSites(data || []);
    } catch (err) {
      console.error('Error fetching WordPress sites:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch WordPress sites');
      toast.error('Failed to load WordPress sites');
    } finally {
      setLoading(false);
    }
  };
  
  // Handle form input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Start editing a site
  const startEdit = (site: WordPressSite) => {
    setFormData({
      domain: site.domain,
      url: site.url,
      username: site.username,
      app_password: site.app_password
    });
    setEditingId(site.id);
    setShowForm(true);
  };
  
  // Cancel editing/adding
  const cancelForm = () => {
    setFormData(emptyForm);
    setEditingId(null);
    setShowForm(false);
    setError(null);
  };
  
  // Validate form data
  const validateForm = () => {
    if (!formData.domain.trim()) {
      setError('Domain is required');
      return false;
    }
    
    if (!formData.url.trim()) {
      setError('URL is required');
      return false;
    }
    
    if (!formData.url.startsWith('http')) {
      setError('URL must start with http:// or https://');
      return false;
    }
    
    if (!formData.username.trim()) {
      setError('Username is required');
      return false;
    }
    
    if (!formData.app_password.trim()) {
      setError('Application password is required');
      return false;
    }
    
    return true;
  };
  
  // Save WordPress site (create or update)
  const saveSite = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      setFormLoading(true);
      setError(null);
      
      const now = new Date().toISOString();
      
      if (editingId) {
        // Update existing site
        const { error } = await supabase
          .from('wordpress_sites')
          .update({
            domain: formData.domain,
            url: formData.url,
            username: formData.username,
            app_password: formData.app_password,
            updated_at: now
          })
          .eq('id', editingId);
        
        if (error) throw new Error(error.message);
        
        toast.success('WordPress site updated successfully');
      } else {
        // Create new site
        const { error } = await supabase
          .from('wordpress_sites')
          .insert({
            domain: formData.domain,
            url: formData.url,
            username: formData.username,
            app_password: formData.app_password,
            created_at: now
          });
        
        if (error) throw new Error(error.message);
        
        toast.success('WordPress site added successfully');
      }
      
      // Reset form and refresh data
      setFormData(emptyForm);
      setEditingId(null);
      setShowForm(false);
      fetchWordPressSites();
      
    } catch (err) {
      console.error('Error saving WordPress site:', err);
      setError(err instanceof Error ? err.message : 'Failed to save WordPress site');
      toast.error('Failed to save WordPress site');
    } finally {
      setFormLoading(false);
    }
  };
  
  // Delete WordPress site
  const deleteSite = async (id: string) => {
    if (!confirm('Are you sure you want to delete this WordPress site? This may affect content publishing.')) {
      return;
    }
    
    try {
      setLoading(true);
      
      const { error } = await supabase
        .from('wordpress_sites')
        .delete()
        .eq('id', id);
      
      if (error) throw new Error(error.message);
      
      toast.success('WordPress site deleted successfully');
      fetchWordPressSites();
      
    } catch (err) {
      console.error('Error deleting WordPress site:', err);
      toast.error('Failed to delete WordPress site');
    } finally {
      setLoading(false);
    }
  };
  
  // Test WordPress connection
  const testConnection = async (site: WordPressSite) => {
    try {
      setTestingConnection(site.id);
      
      // Ensure URL has proper format
      let apiUrl = site.url;
      if (!apiUrl.endsWith('/')) {
        apiUrl += '/';
      }
      if (!apiUrl.includes('wp-json')) {
        apiUrl += 'wp-json/';
      }
      
      // Test connection to WordPress API
      const response = await fetch(`${apiUrl}wp/v2/users/me`, {
        headers: {
          'Authorization': 'Basic ' + btoa(`${site.username}:${site.app_password}`)
        }
      });
      
      if (!response.ok) {
        throw new Error(`WordPress connection failed: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      toast.success(`Connected successfully to ${site.domain} as ${data.name}`);
      
    } catch (err) {
      console.error('WordPress connection test failed:', err);
      toast.error(`Connection to ${site.domain} failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setTestingConnection(null);
    }
  };

  // Bootstrap (scaffold) WordPress site
  const bootstrapSite = async (site: WordPressSite) => {
    try {
      setBootstrappingSite(site.id);
      const now = new Date().toISOString();
      const taskId = uuidv4();

      // Insert agent task row
      const { error } = await supabase.from('agent_status').insert({
        id: taskId,
        content_id: site.id,
        agent: 'site-scaffold-agent',
        status: 'queued',
        input: {},
        created_at: now
      });

      if (error) throw new Error(error.message);

      toast.success(`Bootstrap queued for ${site.domain}`);
      // Optionally update site status here if backend trigger not present
      fetchWordPressSites();
    } catch (err) {
      console.error('Error bootstrapping site:', err);
      toast.error(
        err instanceof Error ? err.message : 'Failed to queue bootstrap task'
      );
    } finally {
      setBootstrappingSite(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
          <FiGlobe className="mr-2" />
          WordPress Sites
        </h2>
        
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
          >
            <FiPlus className="mr-1.5" />
            Add Site
          </button>
        )}
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-3 bg-red-50 border border-red-300 rounded-md text-red-800 text-sm flex items-center">
          <FiAlertCircle className="mr-2 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Add/Edit form */}
      {showForm && (
        <div className="bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h3 className="text-md font-medium mb-3 text-gray-900 dark:text-white">
            {editingId ? 'Edit WordPress Site' : 'Add WordPress Site'}
          </h3>
          
          <form onSubmit={saveSite} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Domain */}
              <div>
                <label htmlFor="domain" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Domain Name *
                </label>
                <input
                  type="text"
                  id="domain"
                  name="domain"
                  value={formData.domain}
                  onChange={handleChange}
                  placeholder="example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  The domain name without protocol (e.g., example.com)
                </p>
              </div>
              
              {/* URL */}
              <div>
                <label htmlFor="url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  WordPress URL *
                </label>
                <input
                  type="url"
                  id="url"
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                  placeholder="https://example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  The full URL with protocol (e.g., https://example.com)
                </p>
              </div>
              
              {/* Username */}
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Username *
                </label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="admin"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
              </div>
              
              {/* App Password */}
              <div>
                <label htmlFor="app_password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Application Password *
                </label>
                <input
                  type="password"
                  id="app_password"
                  name="app_password"
                  value={formData.app_password}
                  onChange={handleChange}
                  placeholder="xxxx xxxx xxxx xxxx"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  required
                />
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Create an application password in WordPress under Users → Profile
                </p>
              </div>
            </div>
            
            {/* Form buttons */}
            <div className="flex justify-end space-x-3 pt-2">
              <button
                type="button"
                onClick={cancelForm}
                className="px-3 py-1.5 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-100 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={formLoading}
                className="inline-flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
              >
                {formLoading ? (
                  <>
                    <FiRefreshCw className="animate-spin mr-1.5" />
                    Saving...
                  </>
                ) : (
                  <>
                    <FiSave className="mr-1.5" />
                    {editingId ? 'Update Site' : 'Add Site'}
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}
      
      {/* Sites table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
        {loading && !sites.length ? (
          <div className="flex justify-center items-center py-8">
            <FiRefreshCw className="animate-spin text-blue-600 mr-2" />
            <span className="text-gray-600 dark:text-gray-300">Loading WordPress sites...</span>
          </div>
        ) : sites.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Domain
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    URL
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Username
                  </th>
                  <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                {sites.map((site) => (
                  <tr key={site.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center">
                        <FiGlobe className="mr-2 text-gray-500 dark:text-gray-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">{site.domain}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <a 
                        href={site.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 flex items-center"
                      >
                        <FiLink className="mr-1" />
                        {site.url}
                      </a>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {site.username}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end space-x-2">
                        <button
                          onClick={() => testConnection(site)}
                          disabled={testingConnection === site.id}
                          className="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                          title="Test Connection"
                        >
                          {testingConnection === site.id ? (
                            <FiRefreshCw className="animate-spin" size={18} />
                          ) : (
                            <FiCheck size={18} />
                          )}
                        </button>
                        {(site.scaffold_status !== 'in_progress' &&
                          site.scaffold_status !== 'done') && (
                          <button
                            onClick={() => bootstrapSite(site)}
                            disabled={bootstrappingSite === site.id}
                            className="text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300"
                            title="Bootstrap Site"
                          >
                            {bootstrappingSite === site.id ? (
                              <FiRefreshCw className="animate-spin" size={18} />
                            ) : (
                              <FiZap size={18} />
                            )}
                          </button>
                        )}
                        <button
                          onClick={() => startEdit(site)}
                          className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                          title="Edit Site"
                        >
                          <FiEdit2 size={18} />
                        </button>
                        <button
                          onClick={() => deleteSite(site.id)}
                          className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                          title="Delete Site"
                        >
                          <FiTrash2 size={18} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-gray-500 dark:text-gray-400">
            <p>No WordPress sites configured yet.</p>
            <p className="text-sm mt-2">
              Click the "Add Site" button to connect your first WordPress site.
            </p>
          </div>
        )}
      </div>
      
      <div className="text-sm text-gray-500 dark:text-gray-400">
        <p>
          <strong>Note:</strong> Each strategic plan must be associated with a WordPress site for publishing.
          Make sure to add your WordPress sites before creating strategic plans.
        </p>
      </div>
    </div>
  );
}
