import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  CircularProgress,
  Tabs,
  Tab,
  Tooltip,
  Snackbar,
} from '@mui/material';
import {
  AccountBalance,
  Phone,
  Send,
  Receipt,
  TrendingUp,
  Refresh,
  QrCode,
  Download,
  WhatsApp,
} from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import { useAuth } from '../../contexts/AuthContext';
import { mpesaAPI } from '../../services/api';

const MpesaDashboard = () => {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [config, setConfig] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [stkDialogOpen, setStkDialogOpen] = useState(false);
  const [stkData, setStkData] = useState({
    phone_number: '',
    amount: '',
    account_reference: '',
  });
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, transactionsRes, configRes] = await Promise.all([
        mpesaAPI.getDashboardStats(token),
        mpesaAPI.getTransactions(token),
        mpesaAPI.getConfig(token),
      ]);
      setStats(statsRes);
      setTransactions(transactionsRes.results || []);
      setConfig(configRes);
    } catch (error) {
      console.error('Error fetching data:', error);
      showSnackbar('Failed to load M-Pesa data', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showSnackbar = (message, severity = 'success') => {
    setSnackbar({ open: true, message, severity });
  };

  const handleSendSTK = async () => {
    if (!stkData.phone_number || !stkData.amount || !stkData.account_reference) {
      showSnackbar('Please fill all fields', 'error');
      return;
    }

    try {
      const response = await mpesaAPI.sendSTKPush(token, stkData);
      showSnackbar(response.message || 'STK Push sent successfully!');
      setStkDialogOpen(false);
      setStkData({ phone_number: '', amount: '', account_reference: '' });
    } catch (error) {
      showSnackbar(error.message || 'Failed to send STK Push', 'error');
    }
  };

  const handleSimulatePayment = async () => {
    const data = {
      phone_number: stkData.phone_number,
      amount: parseFloat(stkData.amount),
      account_reference: stkData.account_reference,
      customer_name: 'Customer',
    };
    
    try {
      const response = await mpesaAPI.simulatePayment(token, data);
      showSnackbar(response.message);
      fetchData(); // Refresh data
    } catch (error) {
      showSnackbar('Failed to simulate payment', 'error');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // Chart data
  const lineChartData = {
    labels: stats?.daily_breakdown?.map(d => d.date) || [],
    datasets: [
      {
        label: 'Daily Transactions (KES)',
        data: stats?.daily_breakdown?.map(d => d.total) || [],
        borderColor: '#2E7D32',
        backgroundColor: 'rgba(46, 125, 50, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'bottom' },
      tooltip: { callbacks: { label: (ctx) => `KES ${ctx.raw.toLocaleString()}` } },
    },
    scales: {
      y: { ticks: { callback: (value) => `KES ${value.toLocaleString()}` } },
    },
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">M-Pesa Integration</Typography>
        <Box>
          <Tooltip title="Refresh">
            <IconButton onClick={fetchData} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<Send />}
            onClick={() => setStkDialogOpen(true)}
            sx={{ ml: 1 }}
          >
            Send STK Push
          </Button>
        </Box>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Transactions (30d)
              </Typography>
              <Typography variant="h4">{stats?.total_transactions || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Amount
              </Typography>
              <Typography variant="h4" color="primary">
                KES {(stats?.total_amount || 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Average Transaction
              </Typography>
              <Typography variant="h4">
                KES {(stats?.average_transaction || 0).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Paybill Number
              </Typography>
              <Typography variant="h4">{config?.business_shortcode || '123456'}</Typography>
              <Typography variant="caption" color="textSecondary">
                {config?.business_name}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Chart */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Transaction Trend (Last 30 Days)
              </Typography>
              <Box height={300}>
                <Line data={lineChartData} options={chartOptions} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs for Transactions */}
      <Card>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}>
          <Tab label="Recent Transactions" />
          <Tab label="STK Push History" />
        </Tabs>

        <Box p={2}>
          {tabValue === 0 && (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Transaction ID</TableCell>
                    <TableCell>Customer</TableCell>
                    <TableCell>Phone</TableCell>
                    <TableCell align="right">Amount (KES)</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {transactions.map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {tx.transaction_id}
                        </Typography>
                      </TableCell>
                      <TableCell>{tx.customer_name || 'N/A'}</TableCell>
                      <TableCell>{tx.customer_phone}</TableCell>
                      <TableCell align="right">
                        <Typography fontWeight="bold">
                          KES {parseFloat(tx.amount).toLocaleString()}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {new Date(tx.transaction_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={tx.status}
                          color={tx.status === 'COMPLETED' ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Send receipt via WhatsApp">
                          <IconButton size="small" color="primary">
                            <WhatsApp fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                  {transactions.length === 0 && (
                    <TableRow>
                      <TableCell colSpan={7} align="center">
                        <Typography color="textSecondary">No transactions found</Typography>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          )}
          {tabValue === 1 && (
            <Typography color="textSecondary" align="center" py={4}>
              STK Push history will appear here
            </Typography>
          )}
        </Box>
      </Card>

      {/* STK Push Dialog */}
      <Dialog open={stkDialogOpen} onClose={() => setStkDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <Box display="flex" alignItems="center">
            <Send sx={{ mr: 1, color: '#2E7D32' }} />
            Send STK Push to Customer
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Alert severity="info" sx={{ mb: 2 }}>
              Customer will receive an M-Pesa prompt on their phone
            </Alert>
            <TextField
              fullWidth
              label="Phone Number"
              placeholder="254711223344"
              value={stkData.phone_number}
              onChange={(e) => setStkData({ ...stkData, phone_number: e.target.value })}
              margin="normal"
              helperText="Format: 254XXXXXXXXX"
            />
            <TextField
              fullWidth
              label="Amount (KES)"
              type="number"
              placeholder="1000"
              value={stkData.amount}
              onChange={(e) => setStkData({ ...stkData, amount: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Account Reference / Invoice Number"
              placeholder="INV-001"
              value={stkData.account_reference}
              onChange={(e) => setStkData({ ...stkData, account_reference: e.target.value })}
              margin="normal"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStkDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSimulatePayment} variant="outlined">
            Simulate Payment
          </Button>
          <Button onClick={handleSendSTK} variant="contained" color="primary">
            Send STK Push
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} onClose={() => setSnackbar({ ...snackbar, open: false })}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default MpesaDashboard;