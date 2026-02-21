'use client';

import { useState, useEffect } from 'react';

interface DashboardMetrics {
  total_money_out: number;
  total_collections: number;
  total_accounts: number;
  active_accounts: number;
  npa_accounts: number;
  pending_interest_charges: number;
}

interface VillageData {
  village: string;
  total_outstanding: number;
  total_collections: number;
  total_customers: number;
  active_accounts: number;
  npa_accounts: number;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardMetrics | null>(null);
  const [villages, setVillages] = useState<string[]>([]);
  const [selectedVillage, setSelectedVillage] = useState<string>('');
  const [villageData, setVillageData] = useState<VillageData | null>(null);
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<'hi' | 'en'>('hi');

  const translations = {
    hi: {
      title: 'संष्केप संज संग्रह',
      global: 'संपूर्ण रिपोर्थ',
      village: 'गपंद संस परित',
      select_village: 'पंचायत सलेखते हैं',
      total_out: 'कुल वितरण',
      collections: 'कुल संग्रह',
      accounts: 'सक्रिय खाते',
      npa_count: 'NPA खाते',
      pending_interest: 'लंबित ब्यांज',
    },
    en: {
      title: 'Analytics Dashboard',
      global: 'Global Summary',
      village: 'Village Analysis',
      select_village: 'Select Village',
      total_out: 'Total Money Out',
      collections: 'Total Collections',
      accounts: 'Active Accounts',
      npa_count: 'NPA Accounts',
      pending_interest: 'Pending Interest',
    },
  };

  const t = translations[language];

  useEffect(() => {
    fetchDashboardSummary();
    fetchVillages();
  }, []);

  const fetchDashboardSummary = async () => {
    try {
      const response = await fetch('/api/analytics/dashboard/summary');
      if (response.ok) {
        const data = await response.json();
        setSummary(data.macro_view);
      }
    } catch (error) {
      console.error('Error fetching dashboard summary:', error);
    }
  };

  const fetchVillages = async () => {
    try {
      const response = await fetch('/api/analytics/villages/list');
      if (response.ok) {
        const data = await response.json();
        setVillages(data.villages || []);
      }
    } catch (error) {
      console.error('Error fetching villages:', error);
    }
  };

  const handleVillageSelect = async (village: string) => {
    setSelectedVillage(village);
    setLoading(true);
    try {
      const response = await fetch(`/api/analytics/dashboard/village/${village}`);
      if (response.ok) {
        const data = await response.json();
        setVillageData(data.data);
      }
    } catch (error) {
      console.error('Error fetching village data:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ label, value, color }: any) => (
    <div className="bg-white p-4 rounded-lg shadow-md" style={{ borderTop: `3px solid ${color}` }}>
      <p className="text-sm text-gray-600 mb-2" style={{ fontFamily: 'Hind, sans-serif' }}>
        {label}
      </p>
      <p className="text-2xl font-bold" style={{ color, fontFamily: 'Mukta, sans-serif' }}>
        {typeof value === 'number' ? `₹${value.toLocaleString('en-IN')}` : value}
      </p>
    </div>
  );

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#fafafa' }}>
      {/* Header */}
      <div style={{ backgroundColor: '#EA580C' }} className="text-white">
        <div className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
          <h1 className="text-3xl font-bold" style={{ fontFamily: 'Mukta, sans-serif' }}>
            {t.title}
          </h1>
          <button
            onClick={() => setLanguage(language === 'hi' ? 'en' : 'hi')}
            className="px-4 py-2 bg-white text-orange-600 rounded font-semibold"
            style={{ fontFamily: 'Hind, sans-serif' }}
          >
            {language === 'hi' ? 'English' : 'हिंदी'}
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Global Summary Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Mukta, sans-serif', color: '#EA580C' }}>
            {t.global}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {summary && [
              { label: t.total_out, value: summary.total_money_out, color: '#EA580C' },
              { label: t.collections, value: summary.total_collections, color: '#4CAF50' },
              { label: t.accounts, value: summary.active_accounts, color: '#2196F3' },
              { label: t.npa_count, value: summary.npa_accounts, color: '#F44336' },
              { label: t.pending_interest, value: summary.pending_interest_charges, color: '#FF9800' },
            ].map((metric, idx) => (
              <MetricCard key={idx} {...metric} />
            ))}
          </div>
        </div>

        {/* Village Filter Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Mukta, sans-serif', color: '#EA580C' }}>
            {t.village}
          </h2>
          <div className="bg-white p-4 rounded-lg shadow-md mb-4">
            <label className="block text-sm font-semibold mb-2" style={{ fontFamily: 'Mukta, sans-serif' }}>
              {t.select_village}
            </label>
            <select
              value={selectedVillage}
              onChange={(e) => handleVillageSelect(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded"
              style={{ fontFamily: 'Hind, sans-serif' }}
            >
              <option value="">पंचायत आव {language === 'hi' ? 'Select' : 'Select'}...</option>
              {villages.map((village) => (
                <option key={village} value={village}>
                  {village}
                </option>
              ))}
            </select>
          </div>

          {/* Village Data */}
          {villageData && selectedVillage && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <MetricCard label={`${t.total_out}`} value={villageData.total_outstanding} color="#EA580C" />
              <MetricCard label={`${t.collections}`} value={villageData.total_collections} color="#4CAF50" />
              <MetricCard label={"कुल ग्राहक"} value={villageData.total_customers} color="#2196F3" />
              <MetricCard label={`${t.accounts}`} value={villageData.active_accounts} color="#9C27B0" />
              <MetricCard label={`${t.npa_count}`} value={villageData.npa_accounts} color="#F44336" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
