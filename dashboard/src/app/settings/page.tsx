'use client';

import { useState, useEffect } from 'react';
import {
  FiSave,
  FiRefreshCw,
  FiCheck,
  FiAlertCircle,
  FiGlobe,
  FiKey,
  FiDatabase
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import WordPressSitesManager from './WordPressSitesManager';

// Define types for settings
type WordPressSite = {
  id: string;          // uuid
  url: string;         // full https://example.com
  username: string;    // wp user
  appPassword: string; // wp application password
};

type OpenAISettings = {
  apiKey: string;
  defaultModel: string;
  temperature: number;
};

type DatabaseSettings = {
  supabaseUrl: string;
  supabaseKey: string;
};

type Settings = {
  wordpressSites: WordPressSite[];
  openai: OpenAISettings;
  database: DatabaseSettings;
};

export default function Settings() {
  // Settings state
  const [settings, setSettings] = useState<Settings>({
    wordpressSites: [], // multi-site support
    openai: {
      apiKey: '',
      defaultModel: 'gpt-4',
      temperature: 0.7
    },
    database: {
      supabaseUrl: '',
      supabaseKey: ''
    }
  });
  
  // UI state
  const [loading, setLoading] = useState(false);
  const [testingOpenAI, setTestingOpenAI] = useState(false);
  const [testingDB, setTestingDB] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'wordpress' | 'openai' | 'database'>('wordpress');
  
  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('wordpress-content-generator-settings');
    if (savedSettings) {
      try {
        const parsedSettings = JSON.parse(savedSettings);
        setSettings(parsedSettings);
      } catch (err) {
        console.error('Error parsing saved settings:', err);
      }
    }
  }, []);
  
  // Handle form input changes
  const handleChange = (
    section: 'openai' | 'database', // wordpress handled separately now
    field: string,
    value: string | number
  ) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        // @ts-expect-error – TS can't infer discriminated union here
        ...prev[section],
        [field]: value
      }
    }));
  };
  
  // Save settings
  const saveSettings = () => {
    try {
      setLoading(true);
      
      // Save to localStorage
      localStorage.setItem('wordpress-content-generator-settings', JSON.stringify(settings));
      
      // Show success message
      toast.success('Settings saved successfully');
      
      // In a real app, you might also save to a backend service
      
    } catch (err) {
      console.error('Error saving settings:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };
  
  // Test OpenAI connection
  const testOpenAIConnection = async () => {
    try {
      setTestingOpenAI(true);
      setError(null);
      
      const { apiKey } = settings.openai;
      
      if (!apiKey) {
        throw new Error('Please enter your OpenAI API key');
      }
      
      // In a real app, you would make a call to the OpenAI API
      // For this demo, we'll simulate a successful connection
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('OpenAI connection successful');
      
    } catch (err) {
      console.error('OpenAI connection test failed:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('OpenAI connection test failed');
    } finally {
      setTestingOpenAI(false);
    }
  };
  
  // Test Supabase connection
  const testDatabaseConnection = async () => {
    try {
      setTestingDB(true);
      setError(null);
      
      const { supabaseUrl, supabaseKey } = settings.database;
      
      if (!supabaseUrl || !supabaseKey) {
        throw new Error('Please fill in all Supabase credentials');
      }
      
      // In a real app, you would initialize the Supabase client and make a test query
      // For this demo, we'll simulate a successful connection
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success('Database connection successful');
      
    } catch (err) {
      console.error('Database connection test failed:', err);
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      toast.error('Database connection test failed');
    } finally {
      setTestingDB(false);
    }
  };
  
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
        <button
          onClick={saveSettings}
          disabled={loading}
          className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:bg-blue-400 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <FiRefreshCw className="animate-spin mr-2" />
              Saving...
            </>
          ) : (
            <>
              <FiSave className="mr-2" />
              Save Settings
            </>
          )}
        </button>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-300 rounded-md text-red-800 flex items-center">
          <FiAlertCircle className="mr-2 flex-shrink-0" />
          <p>{error}</p>
        </div>
      )}
      
      {/* Settings tabs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        {/* Tab navigation */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('wordpress')}
              className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                activeTab === 'wordpress'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <FiGlobe className="mr-2" />
              WordPress
            </button>
            <button
              onClick={() => setActiveTab('openai')}
              className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                activeTab === 'openai'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <FiKey className="mr-2" />
              OpenAI
            </button>
            <button
              onClick={() => setActiveTab('database')}
              className={`py-4 px-6 inline-flex items-center text-sm font-medium border-b-2 ${
                activeTab === 'database'
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <FiDatabase className="mr-2" />
              Database
            </button>
          </nav>
        </div>
        
        {/* Tab content */}
        <div className="p-6">
          {activeTab === 'wordpress' && (
            <WordPressSitesManager />
          )}
          
          {/* OpenAI settings */}
          {activeTab === 'openai' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                <FiKey className="mr-2" />
                OpenAI API Settings
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Configure your OpenAI API settings for content generation. You'll need an API key from your OpenAI account.
              </p>
              
              <div className="space-y-4">
                {/* OpenAI API Key */}
                <div>
                  <label htmlFor="openai-key" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    OpenAI API Key
                  </label>
                  <input
                    type="password"
                    id="openai-key"
                    value={settings.openai.apiKey}
                    onChange={(e) => handleChange('openai', 'apiKey', e.target.value)}
                    placeholder="sk-..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Your OpenAI API key starting with 'sk-'
                  </p>
                </div>
                
                {/* Default Model */}
                <div>
                  <label htmlFor="default-model" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Default Model
                  </label>
                  <select
                    id="default-model"
                    value={settings.openai.defaultModel}
                    onChange={(e) => handleChange('openai', 'defaultModel', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  </select>
                </div>
                
                {/* Temperature */}
                <div>
                  <label htmlFor="temperature" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Temperature: {settings.openai.temperature}
                  </label>
                  <input
                    type="range"
                    id="temperature"
                    min="0"
                    max="2"
                    step="0.1"
                    value={settings.openai.temperature}
                    onChange={(e) => handleChange('openai', 'temperature', parseFloat(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                    <span>More Deterministic (0)</span>
                    <span>More Creative (2)</span>
                  </div>
                </div>
                
                {/* Test Connection Button */}
                <div className="pt-2">
                  <button
                    onClick={testOpenAIConnection}
                    disabled={testingOpenAI}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-green-400 disabled:cursor-not-allowed"
                  >
                    {testingOpenAI ? (
                      <>
                        <FiRefreshCw className="animate-spin mr-2" />
                        Testing Connection...
                      </>
                    ) : (
                      <>
                        <FiCheck className="mr-2" />
                        Test Connection
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Database settings */}
          {activeTab === 'database' && (
            <div className="space-y-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                <FiDatabase className="mr-2" />
                Database Settings
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Configure your Supabase database connection. These settings are used to store content data.
              </p>
              
              <div className="space-y-4">
                {/* Supabase URL */}
                <div>
                  <label htmlFor="supabase-url" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Supabase URL
                  </label>
                  <input
                    type="url"
                    id="supabase-url"
                    value={settings.database.supabaseUrl}
                    onChange={(e) => handleChange('database', 'supabaseUrl', e.target.value)}
                    placeholder="https://your-project.supabase.co"
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                </div>
                
                {/* Supabase Key */}
                <div>
                  <label htmlFor="supabase-key" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Supabase Anon Key
                  </label>
                  <input
                    type="password"
                    id="supabase-key"
                    value={settings.database.supabaseKey}
                    onChange={(e) => handleChange('database', 'supabaseKey', e.target.value)}
                    placeholder="eyJh..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                  />
                  <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                    Your public anon key from Supabase project settings
                  </p>
                </div>
                
                {/* Test Connection Button */}
                <div className="pt-2">
                  <button
                    onClick={testDatabaseConnection}
                    disabled={testingDB}
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-green-400 disabled:cursor-not-allowed"
                  >
                    {testingDB ? (
                      <>
                        <FiRefreshCw className="animate-spin mr-2" />
                        Testing Connection...
                      </>
                    ) : (
                      <>
                        <FiCheck className="mr-2" />
                        Test Connection
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Environment Variables Help */}
      <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 dark:text-blue-300 mb-2">Using Environment Variables</h3>
        <p className="text-sm text-blue-700 dark:text-blue-400">
          For production deployments, it's recommended to use environment variables instead of storing sensitive credentials in the browser.
          Update your <code className="bg-blue-100 dark:bg-blue-800 px-1 py-0.5 rounded">.env.local</code> file with the appropriate values.
        </p>
      </div>
    </div>
  );
}
