import React, { useEffect, useState } from 'react';
import { Search, Calendar } from 'lucide-react';
import { supabase } from './supabaseClient';

function History() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Set default dates to today
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];
  
  const [startDate, setStartDate] = useState(todayStr);
  const [endDate, setEndDate] = useState(todayStr);

  const fetchHistory = async () => {
    setLoading(true);
    
    // Set time to start of start_date and end of end_date
    const start = new Date(startDate);
    start.setHours(0, 0, 0, 0);
    
    const end = new Date(endDate);
    end.setHours(23, 59, 59, 999);

    const { data, error } = await supabase
      .from('transactions')
      .select('*, items(name, barcode), users(full_name, role)')
      .gte('created_at', start.toISOString())
      .lte('created_at', end.toISOString())
      .order('created_at', { ascending: false });

    if (data) {
      setTransactions(data);
    } else if (error) {
      console.error("Error fetching transactions:", error);
    }
    
    setLoading(false);
  };

  useEffect(() => {
    fetchHistory();
  }, [startDate, endDate]);

  const getTypeLabel = (type) => {
    switch (type) {
      case 'sell': return { label: 'លក់ចេញ', color: 'var(--primary)', bg: 'rgba(59, 130, 246, 0.2)' };
      case 'undo': return { label: 'ត្រលប់ប្រាក់', color: 'var(--danger)', bg: 'rgba(239, 68, 68, 0.2)' };
      case 'damage': return { label: 'ខូចខាត', color: 'var(--warning)', bg: 'rgba(245, 158, 11, 0.2)' };
      case 'batch_update': return { label: 'កែតម្រូវ', color: 'var(--text-main)', bg: 'rgba(156, 163, 175, 0.2)' };
      case 'restock': return { label: 'បញ្ចូលស្តុក', color: 'var(--success)', bg: 'rgba(16, 185, 129, 0.2)' };
      default: return { label: type, color: 'var(--text-muted)', bg: 'rgba(156, 163, 175, 0.2)' };
    }
  };

  return (
    <div className="animate-fade-in" style={{ paddingBottom: '80px' }}>
      <h3 style={{ marginBottom: '20px', color: 'var(--text-muted)' }}>ប្រវត្តិស្តុក និងការលក់</h3>
      
      <div className="glass-panel" style={{ marginBottom: '20px', padding: '16px' }}>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>ចាប់ពីថ្ងៃទី</label>
            <input 
              type="date" 
              className="input-field" 
              value={startDate} 
              onChange={(e) => setStartDate(e.target.value)}
              style={{ width: '100%', padding: '10px' }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>ដល់ថ្ងៃទី</label>
            <input 
              type="date" 
              className="input-field" 
              value={endDate} 
              onChange={(e) => setEndDate(e.target.value)}
              style={{ width: '100%', padding: '10px' }}
            />
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '0' }}>
        {loading ? (
          <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>កំពុងទាញយកទិន្នន័យ...</div>
        ) : transactions.length === 0 ? (
          <div style={{ padding: '40px 20px', textAlign: 'center', color: 'var(--text-muted)' }}>
            <Calendar size={40} style={{ margin: '0 auto 10px', opacity: 0.5 }} />
            <div>គ្មានប្រតិបត្តិការទេ សម្រាប់កាលបរិច្ឆេទនេះ</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {transactions.map((tx) => {
              const typeInfo = getTypeLabel(tx.type);
              const txDate = new Date(tx.created_at);
              const isDeduction = tx.type === 'sell' || tx.type === 'damage';
              
              return (
                <div key={tx.id} className="list-item" style={{ padding: '16px', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ fontWeight: '600', fontSize: '15px' }}>{tx.items?.name || 'មិនស្គាល់ឈ្មោះ'}</div>
                    <div style={{ 
                      fontWeight: 'bold', 
                      color: isDeduction ? 'var(--danger)' : 'var(--success)',
                      fontSize: '16px'
                    }}>
                      {isDeduction ? '-' : '+'}{tx.quantity}
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '13px', color: 'var(--text-muted)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ 
                        background: typeInfo.bg, 
                        color: typeInfo.color,
                        padding: '4px 8px',
                        borderRadius: '6px',
                        fontSize: '11px',
                        fontWeight: '600'
                      }}>
                        {typeInfo.label}
                      </span>
                      <span>ដោយ: {tx.users?.full_name || 'មិនស្គាល់'}</span>
                    </div>
                    <div>
                      {txDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export default History;
