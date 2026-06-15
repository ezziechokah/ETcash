import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Phone,
  Send,
  WhatsApp,
  Print,
  Download,
  Payment,
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { invoiceAPI, mpesaAPI, whatsappAPI } from '../../services/api';

const InvoiceDetail = () => {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stkDialogOpen, setStkDialogOpen] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [whatsappDialogOpen, setWhatsappDialogOpen] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    fetchInvoice();
  }, [id]);

  const fetchInvoice = async () => {
    try {
      const data = await invoiceAPI.getInvoice(id);
      setInvoice(data);
      setPhoneNumber(data.customer_phone || '');
    } catch (error) {
      setMessage({ text: 'Failed to load invoice', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSendSTK = async () => {
    if (!phoneNumber) {
      setMessage({ text: 'Please enter customer phone number', severity: 'error' });
      return;
    }

    setProcessing(true);
    try {
      const response = await mpesaAPI.sendSTKPush(null, {
        phone_number: phoneNumber,
        amount: invoice.balance_due,
        account_reference: invoice.invoice_number,
      });
      setMessage({ text: response.message, severity: 'success' });
      setStkDialogOpen(false);
    } catch (error) {
      setMessage({ text: 'Failed to send STK Push', severity: 'error' });
    } finally {
      setProcessing(false);
    }
  };

  const handleSendWhatsApp = async () => {
    setProcessing(true);
    try {
      const response = await whatsappAPI.sendInvoice(invoice.id);
      setMessage({ text: response.message || 'Invoice sent via WhatsApp', severity: 'success' });
      setWhatsappDialogOpen(false);
    } catch (error) {
      setMessage({ text: 'Failed to send via WhatsApp', severity: 'error' });
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <CircularProgress />;
  if (!invoice) return <Typography>Invoice not found</Typography>;

  const isPaid = invoice.status === 'PAID';
  const balanceDue = invoice.balance_due || invoice.total_amount;

  return (
    <Box sx={{ p: 3 }}>
      {message && (
        <Alert severity={message.severity} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      <Card>
        <CardContent>
          {/* Header */}
          <Box display="flex" justifyContent="space-between" alignItems="start">
            <Box>
              <Typography variant="h5">Invoice {invoice.invoice_number}</Typography>
              <Typography color="textSecondary">
                {invoice.customer_name}
              </Typography>
            </Box>
            <Chip
              label={invoice.status}
              color={isPaid ? 'success' : 'warning'}
              size="large"
            />
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Amount */}
          <Box textAlign="center" my={3}>
            <Typography variant="h2" color={isPaid ? 'success.main' : 'primary.main'}>
              KES {balanceDue.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {isPaid ? 'Paid in full' : `Due by ${new Date(invoice.due_date).toLocaleDateString()}`}
            </Typography>
          </Box>

          {/* Payment Actions */}
          {!isPaid && (
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="contained"
                  startIcon={<Phone />}
                  onClick={() => setStkDialogOpen(true)}
                  size="large"
                >
                  Send M-Pesa STK Push
                </Button>
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<WhatsApp />}
                  onClick={() => setWhatsappDialogOpen(true)}
                  size="large"
                >
                  Send via WhatsApp
                </Button>
              </Grid>
              <Grid item xs={12} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Payment />}
                  size="large"
                >
                  Record Manual Payment
                </Button>
              </Grid>
            </Grid>
          )}

          {/* Invoice Details */}
          <Typography variant="h6" gutterBottom>Invoice Items</Typography>
          <Grid container spacing={1}>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Subtotal</Typography>
              <Typography>KES {invoice.subtotal?.toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">VAT (16%)</Typography>
              <Typography>KES {invoice.vat_amount?.toLocaleString()}</Typography>
            </Grid>
            <Grid item xs={6}>
              <Typography variant="body2" color="textSecondary">Total</Typography>
              <Typography variant="h6">KES {invoice.total_amount?.toLocaleString()}</Typography>
            </Grid>
            {invoice.amount_paid > 0 && (
              <Grid item xs={6}>
                <Typography variant="body2" color="textSecondary">Amount Paid</Typography>
                <Typography color="success.main">KES {invoice.amount_paid?.toLocaleString()}</Typography>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>

      {/* STK Push Dialog */}
      <Dialog open={stkDialogOpen} onClose={() => setStkDialogOpen(false)}>
        <DialogTitle>Send M-Pesa STK Push</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Customer will receive an M-Pesa prompt on their phone
          </Typography>
          <TextField
            fullWidth
            label="Customer Phone Number"
            placeholder="254711223344"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            margin="normal"
            helperText="Format: 254XXXXXXXXX"
          />
          <TextField
            fullWidth
            label="Amount (KES)"
            value={balanceDue.toLocaleString()}
            disabled
            margin="normal"
          />
          <TextField
            fullWidth
            label="Account Reference"
            value={invoice.invoice_number}
            disabled
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStkDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSendSTK} variant="contained" disabled={processing}>
            {processing ? <CircularProgress size={24} /> : 'Send STK Push'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* WhatsApp Dialog */}
      <Dialog open={whatsappDialogOpen} onClose={() => setWhatsappDialogOpen(false)}>
        <DialogTitle>Send via WhatsApp</DialogTitle>
        <DialogContent>
          <Typography>
            Send invoice {invoice.invoice_number} to {invoice.customer_name} via WhatsApp?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setWhatsappDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSendWhatsApp} variant="contained" disabled={processing}>
            {processing ? <CircularProgress size={24} /> : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default InvoiceDetail;