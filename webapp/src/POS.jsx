import React, { useState, useEffect } from 'react';
import { Camera, Search, ShoppingCart } from 'lucide-react';
import { supabase } from './supabaseClient';

function POS() {
  const [barcode, setBarcode] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentTxns, setRecentTxns] = useState([]);

  // Mock branch ID and user ID for now
  const branchId = '11111111-1111-1111-1111-111111111111'; // Assuming branch 1
  const userId = window.Telegram?.WebApp?.initDataUnsafe?.user?.id || 7309869072;

  useEffect(() => {
    fetchRecentTxns();
  }, []);

  async function fetchRecentTxns() {
    const { data } = await supabase
      .from('transactions')
      .select('*, items(name, price)')
      .eq('user_id', userId)
      .eq('transaction_type', 'sale')
      .order('created_at', { ascending: false })
      .limit(3);
    if (data) setRecentTxns(data);
  }

  const handleScan = () => {
    alert("នឹងបើកកាមេរ៉ាស្កេន...");
  };

  const handleCheckout = async () => {
    if (!barcode) return;
    setLoading(true);

    // 1. Find item
    const { data: itemData } = await supabase
      .from('items')
      .select('id, name, price')
      .eq('barcode', barcode)
      .single();

    if (!itemData) {
      alert('រកមិនឃើញទំនិញបាកូដនេះទេ');
      setLoading(false);
      return;
    }

    // 2. Check stock
    const { data: inventory } = await supabase
      .from('inventory')
      .select('quantity')
      .eq('item_id', itemData.id)
      .eq('branch_id', branchId)
      .single();

    if (!inventory || inventory.quantity <= 0) {
      alert(`ទំនិញ ${itemData.name} អស់ស្តុកហើយ!`);
      setLoading(false);
      return;
    }

    // 3. Deduct stock (simple update for now)
    await supabase
      .from('inventory')
      .update({ quantity: inventory.quantity - 1 })
      .eq('item_id', itemData.id)
      .eq('branch_id', branchId);

    // 4. Record transaction
    await supabase
      .from('transactions')
      .insert({
        item_id: itemData.id,
        branch_id: branchId,
        user_id: userId,
        transaction_type: 'sale',
        quantity: 1,
        status: 'completed'
      });

    alert(`✅ បានលក់ ${itemData.name} ដោយជោគជ័យ!`);
    setBarcode('');
    fetchRecentTxns();
    setLoading(false);
  };

  return (
    <div className="animate-fade-in">
      <div className="glass-panel" style={{marginBottom: '20px', textAlign: 'center'}}>
        <div style={{background: 'rgba(59, 130, 246, 0.1)', width: '80px', height: '80px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: 'var(--primary)', cursor: 'pointer'}} onClick={handleScan}>
          <Camera size={40} />
        </div>
        <h3 style={{margin: '0 0 8px'}}>ចុចទីនេះដើម្បីស្កេន</h3>
        <p style={{color: 'var(--text-muted)', fontSize: '14px', margin: 0}}>ប្រើប្រាស់កាមេរ៉ាទូរស័ព្ទរបស់អ្នក</p>
      </div>

      <div style={{position: 'relative', marginBottom: '20px'}}>
        <input 
          type="text" 
          className="input-field" 
          placeholder="ឬ វាយបញ្ចូលលេខបាកូដ..." 
          value={barcode}
          onChange={(e) => setBarcode(e.target.value)}
          style={{paddingLeft: '40px'}}
        />
        <Search size={20} color="var(--text-muted)" style={{position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)'}} />
      </div>

      <button className="btn" onClick={handleCheckout} disabled={!barcode || loading} style={{opacity: (!barcode || loading) ? 0.5 : 1}}>
        <ShoppingCart size={20} /> {loading ? 'កំពុងទូទាត់...' : 'កាត់ស្តុកលក់ (Checkout)'}
      </button>

      {/* Cart Items Placeholder */}
      <div style={{marginTop: '30px'}}>
        <h4 style={{marginBottom: '16px', color: 'var(--text-muted)'}}>ប្រវត្តិលក់ថ្មីៗរបស់អ្នក</h4>
        <div className="glass-panel" style={{padding: '0'}}>
          {recentTxns.length === 0 ? (
            <div style={{padding: '16px', textAlign: 'center', color: 'var(--text-muted)'}}>មិនទាន់មានប្រវត្តិលក់ទេ</div>
          ) : (
            recentTxns.map((txn, idx) => (
              <div key={idx} className="list-item">
                <div>
                  <div style={{fontWeight: '600'}}>{txn.items?.name || 'មិនស្គាល់'}</div>
                  <div style={{fontSize: '12px', color: 'var(--text-muted)'}}>{txn.quantity} x ${txn.items?.price}</div>
                </div>
                <div style={{fontSize: '12px', color: 'var(--success)'}}>ជោគជ័យ</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default POS;
