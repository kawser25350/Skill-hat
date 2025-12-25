"""
SSLCommerz Payment Gateway Integration
Supports: bKash, Nagad, Rocket, Visa, MasterCard, etc.

Sandbox (Testing) is FREE
Production requires merchant account
"""
import requests
import uuid
from django.conf import settings
from decimal import Decimal


class SSLCommerzPayment:
    """SSLCommerz Payment Gateway Handler"""
    
    def __init__(self, sandbox=True):
        self.sandbox = sandbox
        
        if sandbox:
            self.base_url = "https://sandbox.sslcommerz.com"
            self.store_id = getattr(settings, 'SSLCOMMERZ_STORE_ID', 'skill60db2d47a6db1')
            self.store_pass = getattr(settings, 'SSLCOMMERZ_STORE_PASSWORD', 'skill60db2d47a6db1@ssl')
        else:
            self.base_url = "https://securepay.sslcommerz.com"
            self.store_id = settings.SSLCOMMERZ_STORE_ID
            self.store_pass = settings.SSLCOMMERZ_STORE_PASSWORD
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        return f"SKILLHAT_{uuid.uuid4().hex[:12].upper()}"
    
    def initiate_payment(self, booking, success_url, fail_url, cancel_url, ipn_url=None):
        """
        Initiate payment session with SSLCommerz
        Returns payment URL to redirect user
        """
        from core.models import Payment
        
        # Generate transaction ID
        tran_id = self.generate_transaction_id()
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.estimated_price,
            transaction_id=tran_id,
            status='initiated'
        )
        
        # Prepare payload
        payload = {
            'store_id': self.store_id,
            'store_passwd': self.store_pass,
            'total_amount': str(booking.estimated_price),
            'currency': 'BDT',
            'tran_id': tran_id,
            'success_url': success_url,
            'fail_url': fail_url,
            'cancel_url': cancel_url,
            'ipn_url': ipn_url or success_url,
            
            # Customer info
            'cus_name': booking.client.get_full_name() or booking.client.username,
            'cus_email': booking.client.email or f'{booking.client.username}@skillhat.com',
            'cus_phone': booking.phone or '01700000000',
            'cus_add1': booking.location,
            'cus_city': 'Dhaka',
            'cus_country': 'Bangladesh',
            
            # Shipping info (same as customer)
            'shipping_method': 'NO',
            'num_of_item': 1,
            
            # Product info
            'product_name': f'Booking #{booking.id} - {booking.title}',
            'product_category': 'Service',
            'product_profile': 'general',
            
            # Optional - EMI
            'emi_option': 0,
            
            # Value fields
            'value_a': str(booking.id),  # Booking ID
            'value_b': str(payment.id),  # Payment ID
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/gwprocess/v4/api.php",
                data=payload,
                timeout=30
            )
            
            data = response.json()
            
            if data.get('status') == 'SUCCESS':
                # Update payment with session key
                payment.session_key = data.get('sessionkey', '')
                payment.status = 'pending'
                payment.save()
                
                return {
                    'success': True,
                    'payment_url': data.get('GatewayPageURL'),
                    'session_key': data.get('sessionkey'),
                    'transaction_id': tran_id,
                    'payment_id': payment.id
                }
            else:
                payment.status = 'failed'
                payment.gateway_response = data
                payment.save()
                
                return {
                    'success': False,
                    'error': data.get('failedreason', 'Payment initiation failed'),
                    'transaction_id': tran_id
                }
                
        except Exception as e:
            payment.status = 'failed'
            payment.gateway_response = {'error': str(e)}
            payment.save()
            
            return {
                'success': False,
                'error': str(e),
                'transaction_id': tran_id
            }
    
    def validate_payment(self, val_id):
        """
        Validate payment after successful transaction
        Call this on success URL to verify payment
        """
        try:
            response = requests.get(
                f"{self.base_url}/validator/api/validationserverAPI.php",
                params={
                    'val_id': val_id,
                    'store_id': self.store_id,
                    'store_passwd': self.store_pass,
                    'format': 'json'
                },
                timeout=30
            )
            
            data = response.json()
            
            return {
                'success': data.get('status') == 'VALID' or data.get('status') == 'VALIDATED',
                'data': data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_ipn(self, post_data):
        """
        Process Instant Payment Notification (IPN)
        Called by SSLCommerz after payment
        """
        from core.models import Payment
        from django.utils import timezone
        
        tran_id = post_data.get('tran_id')
        status = post_data.get('status')
        val_id = post_data.get('val_id')
        
        try:
            payment = Payment.objects.get(transaction_id=tran_id)
            
            # Update payment details
            payment.val_id = val_id or ''
            payment.bank_tran_id = post_data.get('bank_tran_id', '')
            payment.card_type = post_data.get('card_type', '')
            payment.card_brand = post_data.get('card_brand', '')
            payment.payment_method = self._map_card_type(post_data.get('card_type', ''))
            payment.gateway_response = dict(post_data)
            
            if status == 'VALID' or status == 'VALIDATED':
                # Validate payment
                validation = self.validate_payment(val_id)
                
                if validation['success']:
                    payment.status = 'completed'
                    payment.paid_at = timezone.now()
                    
                    # Update booking
                    booking = payment.booking
                    booking.payment_status = 'paid'
                    booking.status = 'confirmed'
                    booking.save()
                else:
                    payment.status = 'failed'
                    
            elif status == 'FAILED':
                payment.status = 'failed'
                payment.booking.payment_status = 'failed'
                payment.booking.save()
                
            elif status == 'CANCELLED':
                payment.status = 'cancelled'
                
            payment.save()
            
            return {
                'success': payment.status == 'completed',
                'payment': payment
            }
            
        except Payment.DoesNotExist:
            return {
                'success': False,
                'error': 'Payment not found'
            }
    
    def _map_card_type(self, card_type):
        """Map SSLCommerz card type to our payment method"""
        card_type_lower = card_type.lower() if card_type else ''
        
        mapping = {
            'bkash': 'bkash',
            'nagad': 'nagad',
            'rocket': 'rocket',
            'upay': 'upay',
            'visa': 'visa',
            'master': 'master',
            'mastercard': 'master',
            'amex': 'amex',
            'bank': 'bank',
        }
        
        for key, value in mapping.items():
            if key in card_type_lower:
                return value
        
        return 'sslcommerz'


def get_payment_gateway(sandbox=None):
    """Get payment gateway instance"""
    if sandbox is None:
        sandbox = getattr(settings, 'DEBUG', True)
    
    return SSLCommerzPayment(sandbox=sandbox)
