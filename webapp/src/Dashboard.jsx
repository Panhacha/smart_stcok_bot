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
      <h3 style={{marginBottom: '20px', color: 'var(--text-muted)'}}>សេចក្តីសង្ខេបថ្ងៃនេះ</h3>
      
      <div className="card-grid" style={{marginTop: '0'}}>
        <div className="glass-panel" style={{padding: '16px'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px'}}>
            <div className="stat-label">ចំណូលសរុប</div>
            <div style={{padding: '8px', background: 'rgba(16, 185, 129, 0.2)', borderRadius: '8px', color: 'var(--success)'}}>
              <DollarSign size={20} />
            </div>
          </div>
          <div className="stat-value">${revenue.toFixed(2)}</div>
        </div>

        <div className="glass-panel" style={{padding: '16px'}}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px'}}>
            <div className="stat-label">លក់ចេញសរុប</div>
            <div style={{padding: '8px', background: 'rgba(59, 130, 246, 0.2)', borderRadius: '8px', color: 'var(--primary)'}}>
              <PackageMinus size={20} />
            </div>
          </div>
          <div className="stat-value">{itemsSold} មុខ</div>
        </div>
      </div>

      <div className="glass-panel" style={{marginTop: '20px'}}>
        <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px', color: 'var(--warning)'}}>
          <AlertCircle size={20} />
          <h4 style={{margin: 0, color: 'var(--text-main)'}}>ទំនិញជិតអស់ស្តុក</h4>
        </div>
        
        {lowStockItems.length === 0 ? (
          <div style={{color: 'var(--text-muted)', textAlign: 'center', padding: '10px'}}>គ្មានទំនិញជិតអស់ស្តុកទេ</div>
        ) : (
          lowStockItems.map((item, index) => (
            <div key={index} className="list-item" style={{padding: '12px 0'}}>
              <div>
                <div style={{fontWeight: '600'}}>{item.items?.name || 'មិនស្គាល់ឈ្មោះ'}</div>
                <div style={{fontSize: '12px', color: 'var(--text-muted)'}}>បាកូដ: {item.items?.barcode}</div>
              </div>
              <div className="badge" style={{
                background: item.quantity <= 0 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)', 
                color: item.quantity <= 0 ? 'var(--danger)' : 'var(--warning)'
              }}>
                សល់ {item.quantity}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default Dashboard;
