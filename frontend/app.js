const PAY_STATUS_LABEL = {
  unpaid: '🔴 Belum Bayar',
  verifying: '🟡 Menunggu Verifikasi Admin',
  paid: '🟢 Lunas',
  rejected: '❌ Pembayaran Ditolak'
};

function payStatusBadge(s) {
  const cls = s === 'paid' ? 'open' : (s === 'verifying' ? 'boost' : 'closed');
  return `<span class="badge ${cls}">${PAY_STATUS_LABEL[s] || s}</span>`;
}