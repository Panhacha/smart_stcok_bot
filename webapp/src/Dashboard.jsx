import React, { useEffect, useState } from 'react';
import { TrendingUp, PackageMinus, DollarSign, AlertCircle } from 'lucide-react';
import { supabase } from './supabaseClient';

function Dashboard() {
  const [revenue, setRevenue] = useState(0);
  const [itemsSold, setItemsSold] = useState(0);
  const [lowStockItems, setLowStockItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      // Fetch today's transactions
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const { data: txns } = await supabase
        .from('transactions')
        .select('*, items(price)')
        .eq('transaction_type', 'sale')
        .eq('status', 'completed')
        .gte('created_at', today.toISOString());

      if (txns) {
        const totalRev = txns.reduce((sum, tx) => sum + (tx.quantity * (tx.items?.price || 0)), 0);
        const totalItems = txns.reduce((sum, tx) => sum + tx.quantity, 0);
        setRevenue(totalRev);
        setItemsSold(totalItems);
      }

      // Fetch low stock items (<= 10)
      const { data: stock } = await supabase
        .from('inventory')
        .select('*, items(name, barcode)')
        .lte('quantity', 10)
        .order('quantity', { ascending: true })
        .limit(5);

      if (stock) {
        setLowStockItems(stock);
      }
      setLoading(false);
    }
    fetchData();
  }, []);

  if (loading) return <div style={{textAlign: 'center', padding: '20px'}}>កំពុងទាញយកទិន្នន័យ...</div>;

  return (
    <div className="animate-fade-in">
      <h3 style={{marginBottom: '20px', color: 'var(--text-muted)', fontSize: '18px', fontWeight: '500'}}>សេចក្តីសង្ខេបថ្ងៃនេះ</h3>
      
      <div className="card-grid">
        <div className="glass-panel" style={{padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="stat-label">ចំណូលសរុប</div>
            <div style={{padding: '10px', background: 'rgba(16, 185, 129, 0.15)', borderRadius: '12px', color: 'var(--success)'}}>
              <DollarSign size={24} />
            </div>
          </div>
          <div className="stat-value">${revenue.toFixed(2)}</div>
        </div>

        <div className="glass-panel" style={{padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <div className="stat-label">លក់ចេញសរុប</div>
            <div style={{padding: '10px', background: 'rgba(59, 130, 246, 0.15)', borderRadius: '12px', color: 'var(--primary)'}}>
              <PackageMinus size={24} />
            </div>
          </div>
          <div className="stat-value">{itemsSold} មុខ</div>
        </div>
      </div>

      <div className="glass-panel" style={{marginTop: '24px', padding: 0, overflow: 'hidden'}}>
        <div style={{padding: '20px', borderBottom: '1px solid var(--glass-border)'}}>
          <div style={{display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--warning)'}}>
            <AlertCircle size={24} />
            <h3 style={{margin: 0, color: 'var(--text-main)', fontSize: '18px', fontWeight: '600'}}>ទំនិញជិតអស់ស្តុក</h3>
          </div>
        </div>
        
        {lowStockItems.length === 0 ? (
          <div style={{color: 'var(--text-muted)', textAlign: 'center', padding: '32px'}}>គ្មានទំនិញជិតអស់ស្តុកទេ</div>
        ) : (
          <div>
            {lowStockItems.map((item, index) => (
              <div key={index} className="list-item">
                <div style={{display: 'flex', flexDirection: 'column', gap: '4px'}}>
                  <div style={{fontWeight: '600', fontSize: '16px', color: 'var(--text-main)'}}>{item.items?.name || 'មិនស្គាល់ឈ្មោះ'}</div>
                  <div style={{fontSize: '14px', color: 'var(--text-muted)'}}>បាកូដ: {item.items?.barcode}</div>
                </div>
                <div className="badge" style={{
                  background: item.quantity <= 0 ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)', 
                  color: item.quantity <= 0 ? 'var(--danger)' : 'var(--warning)'
                }}>
                  សល់ {item.quantity}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
