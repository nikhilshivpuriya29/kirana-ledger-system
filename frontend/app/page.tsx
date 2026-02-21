'use client';

import { useState } from 'react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'login' | 'register'>('login');
  const [formData, setFormData] = useState({
    phone_number: '',
    pin: '',
    shop_name: '',
    owner_name: '',
    address: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const endpoint = activeTab === 'login' ? '/api/auth/login' : '/api/auth/register';
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(
          activeTab === 'login'
            ? { phone_number: formData.phone_number, pin: formData.pin }
            : formData
        ),
      });

      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('token', data.access_token);
        setMessage('सेथ सढ़गयी | Success!');
        // Redirect to dashboard
        setTimeout(() => window.location.href = '/dashboard', 1500);
      } else {
        setMessage(data.detail || 'An error occurred');
      }
    } catch (error) {
      setMessage('Network error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Card Container */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-4">
            <h2 className="text-2xl font-bold text-white" style={{ fontFamily: 'Mukta, sans-serif' }}>
              {activeTab === 'login' ? 'लॉगइन' : 'बिआ' }
            </h2>
            <p className="text-orange-100 text-sm mt-1">
              {activeTab === 'login'
                ? 'अपनी खाते में वुळि अनुव्मख
                : 'वणरसजे से आमंत्रण करे'}
            </p>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200">
            {(['login', 'register'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`flex-1 py-3 font-semibold transition ${
                  activeTab === tab
                    ? 'bg-orange-50 text-orange-600 border-b-2 border-orange-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                {tab === 'login' ? 'लॉगइन' : 'बिआ'}
              </button>
            ))}
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Phone Number */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                मौहली नंबर | Phone Number
              </label>
              <input
                type="tel"
                name="phone_number"
                placeholder="10-digit number"
                value={formData.phone_number}
                onChange={handleInputChange}
                maxLength={10}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>

            {/* PIN */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                PIN (4 digits)
              </label>
              <input
                type="password"
                name="pin"
                placeholder="0000"
                value={formData.pin}
                onChange={handleInputChange}
                maxLength={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                required
              />
            </div>

            {/* Registration Fields */}
            {activeTab === 'register' && (
              <>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    दुकान के लिए ठसरी | Shop Name
                  </label>
                  <input
                    type="text"
                    name="shop_name"
                    value={formData.shop_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    ढदु स्वीकार | Owner Name
                  </label>
                  <input
                    type="text"
                    name="owner_name"
                    value={formData.owner_name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    पता | Address
                  </label>
                  <textarea
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    rows={2}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    required
                  />
                </div>
              </>
            )}

            {/* Message */}
            {message && (
              <div className={`p-3 rounded-lg text-sm font-semibold ${
                message.includes('Success') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                {message}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold py-2 rounded-lg hover:shadow-lg transition disabled:opacity-50"
            >
              {isLoading ? 'गु॒तॉ सलह हिं | Processing...' : (activeTab === 'login' ? 'लॉगइन' : 'बिआ')}
            </button>
          </form>
        </div>

        {/* Footer Info */}
        <div className="mt-6 text-center text-gray-600 text-sm" style={{ fontFamily: 'Mukta, sans-serif' }}>
          <p className="font-semibold mb-2">बाही-खाता डिजिटल</p>
          <p>The Trusted Munim 💼</p>
          <p className="text-xs mt-2">Phone + PIN भी प्रमाण | UPI Style Authentication</p>
        </div>
      </div>
    </div>
  );
}
