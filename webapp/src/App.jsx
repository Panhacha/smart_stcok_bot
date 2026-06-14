import React, { useEffect, useState } from 'react';
import { LayoutDashboard, History as HistoryIcon, ShoppingCart } from 'lucide-react';
import { supabase } from './supabaseClient';
import Dashboard from './Dashboard';
import POS from './POS';
import History from './History';

function App() {
  const [userRole, setUserRole] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('home'); // 'home' or 'history'
  const tg = window.Telegram?.WebApp;

  useEffect(() => {
    if (tg) {
      tg.ready();
      tg.expand();
      const userId = tg.initDataUnsafe?.user?.id || 7309869072; // Fallback for dev

      async function fetchUser() {
        const { data, error } = await supabase
          .from('users')
          .select('role')
          .eq('telegram_id', userId)
          .single();
        
        if (data) {
          setUserRole(data.role);
        } else {
          setUserRole('unregistered');
        }
        setLoading(false);
      }
      fetchUser();
    }
  }, []);

  if (loading) {
    return <div className="app-container" style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>Loading...</div>;
  }

  if (userRole === 'unregistered') {
    return <div className="app-container"><h2>អ្នកមិនទាន់មានឈ្មោះក្នុងប្រព័ន្ធទេ។</h2></div>;
  }

  const renderContent = () => {
    if (activeTab === 'history') {
      return <History />;
    }
    return userRole === 'owner' ? <Dashboard /> : <POS />;
  };

  const getHeaderTitle = () => {
    if (activeTab === 'history') return 'ប្រវត្តិប្រតិបត្តិការ';
    return userRole === 'owner' ? 'Owner Dashboard' : 'Staff POS';
  };

  return (
    <div>
      <div className="header">
        <h2>{getHeaderTitle()}</h2>
      </div>
      <div className="app-container">
        {renderContent()}
      </div>
      
      <div className="bottom-nav">
        <button 
          className={`nav-btn ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          {userRole === 'owner' ? <LayoutDashboard size={24} /> : <ShoppingCart size={24} />}
          <span>ទំព័រដើម</span>
        </button>
        <button 
          className={`nav-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <HistoryIcon size={24} />
          <span>ប្រវត្តិ</span>
        </button>
      </div>
    </div>
  );
}

export default App;
