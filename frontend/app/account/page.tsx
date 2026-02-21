'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Transaction {
  id: string;
  date: string;
  type: string;
  amount: number;
  status: string;
}

interface Account {
  account_id: string;
  customer_name: string;
  outstanding_balance: number;
  total_paid: number;
  account_status: string;
  transactions: Transaction[];
}

export default function AccountPage() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<Account | null>(null);
  const [searchId, setSearchId] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState<'hi' | 'en'>('hi');

  const translations = {
    hi: {
      title: 'खाता विवरण',
      search: 'खाता खोजें',
      accountId: 'खाता ID',
      customerName: 'ग्राहक का नाम',
      balance: 'बकाया राशि',
      totalPaid: 'कुल भुगतान',
      status: 'स्थिति',
      transactions: 'लेनदेन',
      amount: 'राशि',
      date: 'तारीख',
      type: 'प्रकार',
      active: 'सक्रिय',
      addTransaction: 'लेनदेन जोड़ें',
      payment: 'भुगतान करें',
      search_placeholder: 'खाता ID या फोन दर्ज करें...',
    },
    en: {
      title: 'Account Record',
      search: 'Search Account',
      accountId: 'Account ID',
      customerName: 'Customer Name',
      balance: 'Outstanding Balance',
      totalPaid: 'Total Paid',
      status: 'Status',
      transactions: 'Transactions',
      amount: 'Amount',
      date: 'Date',
      type: 'Type',
      active: 'Active',
      addTransaction: 'Add Transaction',
      payment: 'Make Payment',
      search_placeholder: 'Enter account ID or phone...',
    },
  };

  const t = translations[language];

  const handleSearch = async () => {
    if (!searchId.trim()) return;
    setLoading(true);
    try {
      const response = await fetch(`/api/ledger/account/${searchId}/statement`);
      if (response.ok) {
        const data = await response.json();
        setSelectedAccount(data);
      }
    } catch (error) {
      console.error('Error fetching account:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#fafafa' }}>
      {/* Header with Hindi/English toggle */}
      <div className="sticky top-0 z-10" style={{ backgroundColor: '#EA580C' }}>
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Mukta, sans-serif' }}>
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

      {/* Search Section */}
      <div className="max-w-6xl mx-auto px-4 py-6">
        <div className="bg-white p-6 rounded-lg shadow-md" style={{ borderLeft: '4px solid #EA580C' }}>
          <label className="block text-sm font-semibold mb-2" style={{ fontFamily: 'Mukta, sans-serif' }}>
            {t.search}
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={t.search_placeholder}
              className="flex-1 px-4 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2"
              style={{ fontFamily: 'Hind, sans-serif', '--tw-ring-color': '#EA580C' } as any}
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 text-white rounded font-semibold hover:opacity-90 disabled:opacity-50"
              style={{ backgroundColor: '#EA580C', fontFamily: 'Mukta, sans-serif' }}
            >
              {loading ? 'खोज रहे हैं...' : t.search}
            </button>
          </div>
        </div>
      </div>

      {/* Account Details - Paper Stack Card Design */}
      {selectedAccount && (
        <div className="max-w-6xl mx-auto px-4 pb-8">
          {/* Main Card */}
          <div className="relative mb-8">
            {/* Shadow layers for paper stack effect */}
            <div
              className="absolute top-2 left-2 right-2 bottom-2 rounded-lg"
              style={{ backgroundColor: '#f5f5f5', zIndex: 1 }}
            />
            <div
              className="absolute top-1 left-1 right-1 bottom-1 rounded-lg"
              style={{ backgroundColor: '#fafafa', zIndex: 2 }}
            />

            {/* Main Content */}
            <div className="relative bg-white p-6 rounded-lg shadow-lg z-3">
              <div className="border-l-4 pb-4" style={{ borderColor: '#EA580C' }}>
                <h2 className="text-2xl font-bold" style={{ fontFamily: 'Mukta, sans-serif', color: '#EA580C' }}>
                  {selectedAccount.customer_name || t.customerName}
                </h2>
                <p className="text-sm text-gray-600" style={{ fontFamily: 'Hind, sans-serif' }}>
                  {t.accountId}: {selectedAccount.account_id}
                </p>
              </div>

              {/* Account Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                {[
                  { label: t.balance, value: selectedAccount.outstanding_balance, color: '#EA580C' },
                  { label: t.totalPaid, value: selectedAccount.total_paid, color: '#4CAF50' },
                  { label: t.status, value: selectedAccount.account_status, color: '#2196F3', isText: true },
                ].map((stat, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded"
                    style={{ backgroundColor: stat.color + '15', borderLeft: `3px solid ${stat.color}` }}
                  >
                    <p className="text-xs text-gray-600 mb-1" style={{ fontFamily: 'Hind, sans-serif' }}>
                      {stat.label}
                    </p>
                    <p className="text-lg font-bold" style={{ color: stat.color, fontFamily: 'Mukta, sans-serif' }}>
                      {stat.isText ? stat.value : `₹${stat.value}`}
                    </p>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6">
                <Link
                  href={`/transaction?account=${selectedAccount.account_id}`}
                  className="flex-1 px-4 py-2 text-white rounded font-semibold text-center hover:opacity-90"
                  style={{ backgroundColor: '#EA580C', fontFamily: 'Mukta, sans-serif' }}
                >
                  {t.addTransaction}
                </Link>
                <Link
                  href={`/payment?account=${selectedAccount.account_id}`}
                  className="flex-1 px-4 py-2 text-white rounded font-semibold text-center hover:opacity-90"
                  style={{ backgroundColor: '#4CAF50', fontFamily: 'Mukta, sans-serif' }}
                >
                  {t.payment}
                </Link>
              </div>
            </div>
          </div>

          {/* Recent Transactions */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-bold mb-4" style={{ fontFamily: 'Mukta, sans-serif', color: '#EA580C' }}>
              {t.transactions}
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full" style={{ fontFamily: 'Hind, sans-serif' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #EA580C' }}>
                    <th className="text-left py-2 px-2">{t.date}</th>
                    <th className="text-left py-2 px-2">{t.type}</th>
                    <th className="text-right py-2 px-2">{t.amount}</th>
                    <th className="text-center py-2 px-2">{t.status}</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedAccount.transactions && selectedAccount.transactions.length > 0 ? (
                    selectedAccount.transactions.map((txn: any) => (
                      <tr key={txn.id} style={{ borderBottom: '1px solid #eee' }}>
                        <td className="py-2 px-2">{new Date(txn.date).toLocaleDateString(language === 'hi' ? 'hi-IN' : 'en-US')}</td>
                        <td className="py-2 px-2">{txn.type}</td>
                        <td className="text-right py-2 px-2 font-semibold">₹{txn.amount}</td>
                        <td className="text-center py-2 px-2">
                          <span
                            className="px-2 py-1 rounded text-xs font-semibold"
                            style={{
                              backgroundColor: txn.status === 'completed' ? '#4CAF5033' : '#FFC10733',
                              color: txn.status === 'completed' ? '#4CAF50' : '#FFC107',
                            }}
                          >
                            {txn.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={4} className="text-center py-4 text-gray-500">
                        {language === 'hi' ? 'कोई लेनदेन नहीं' : 'No transactions'}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!selectedAccount && (
        <div className="max-w-6xl mx-auto px-4 py-16 text-center">
          <p className="text-gray-500 text-lg" style={{ fontFamily: 'Hind, sans-serif' }}>
            {language === 'hi' ? 'खाता विवरण देखने के लिए खाता ID दर्ज करें' : 'Enter account ID to view account details'}
          </p>
        </div>
      )}
    </div>
  );
}
