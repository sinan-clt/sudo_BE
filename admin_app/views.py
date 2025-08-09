import base64
import datetime
import uuid, os
import random
import string
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import firebase_admin
from firebase_admin import credentials, firestore, messaging, auth
import qrcode
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail
from dotenv import load_dotenv
# from google.cloud import firestore



# Load environment variables from .env file
load_dotenv()

# Ensure Firebase is initialized only once
if not firebase_admin._apps:
    # Load Firebase credentials from the environment variables
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "sudo-70852",
        "private_key_id": "5764dd9f77c53703fbc857b21cd625d3e93b42a3",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCz4LIxKDpylIlk\n9wcy5AZ5s0BhPFjqw009T2/fgIHAqPR7cra8ltQinjfyJb3u5aOR6yIPU67AjDgI\ne3Ry8egy0E7S2qejbpZRviPbWPJoROjoUW6LHFoS/tb6BKDpqauVl0s5eI1EVmbC\nMy8bjgTRHmFw/W+N8B3uKPEUgvV186hYzndcadXeEhVN+f3S+rf6Uhouba70Li0T\npc05bijbGkvZYPdjy8Ged2XFd9Y0rFqlrNMM3jOEhvYZs55Vb9Kp3r98uzys2WfH\ni8h4sdy2sXq0AAHQ+rS1juoZgTPZkMeFKqURB8+37a49R5BUBdpfeTDPHaffQUqb\nwJRwUoBpAgMBAAECggEAC8Tn489+A4E0fCatkebZhZz02WfZaYLdyuUnrLf7xV9I\nn8shqbU0rA8uGeneQ4NC8Ikx8U7IYFDMWcG6HMs3Jhv7DFDCJy9VJoQKVI+9TJU1\np/2r/e4c9qE176Xd4Wv4jhEYGuqIU7BTiOFQc70XE5epSHtMkTzkuHB1VaI77Tun\n3Ely7v4uALkzkJF96ZbzPlCyvMsUHvIzFu0a3Eq/xcWCgku9BLl0ELDGmvDkptUv\nQ3AJHf6eA3ieKoXrW6JsbPec5kVq94skEtR/ZZZ1l2P6Uho7psIJJOqgOro8iSyH\nVQ5+C+q+AvSCl4HBseYVEBrpACFy+utkgm4ToNYjAQKBgQDogKVfHuwXMK2RlYP2\nuMsBPgtRPk+nhGdwLP3wIE7MKjHZLitaXs6C9/ELC7A1AP3RfluvH7kqFHoZ5htW\nVBscg0a+vtFssK5oID0vp6jQEMDxiy5IF+HLcUipvC3DDAXXh12AIAlkhqRsO2CR\nearNSVVLiE3w2JebLZjovcWbGwKBgQDGDoe1WSBP79QFDDgHZVvX2pu8q3i4goDi\nkKyIejhuzyjopom2yGx7LeCqQ9bwBjLyqy4As16Wr6eCORUQgmsn29heeujIhk+P\nDuoqXRqIAB1UQlaivQ5o2gT9LeUoAJVqKllgf8CxD7PpaM6QyLKEHr0knhFwjmba\ni5zNMfemywKBgQCV3Q47MNBW5k6Kj4g/CL/5bgeXd4WaYbLW0HliRUDlQrFc3vCc\n0I1mR/D8AK20jI4OcdchG16b7BUECplGXPIYv9li69ZLq9rPTTCDPhuG+bWUO/U6\nDQLCwqNmnOAWX/KICT3Qb1X+kPb8uI03V+graIBtLk+m1cVrBcoRAvmTTwKBgGiH\nsK5Q3NHztQX4/fVBVKjnEv0PzwYqspVhX/4j63boVSH9C3/x5fdZLlMOvPkvfGJB\nYGU0Rf7ntFPxhqGRA7cku9yZqBR1drX9XC+BtggDb3dSD+GSQHGsZ6esOl7TeAhx\nU3yv0GZi8ESHcUZO9pDunEsgNfoe3kAIIXjXH2rjAoGANnqHBwQZzRMdWLnq9iRo\nF1tuj8r+REkFjHiHmYeMFJ31+VV4/yJNkqw3QqHWx9p9T4J69U/DVskZy7pklL+0\nt7TSeGgrK6cyYSAUa2MxIftdh/fXnnTCzpbazADROPLD61cCxZSRqWgZuqSdOXtA\nwD0e4Odss2x6PGrtnt0H5YA=\n-----END PRIVATE KEY-----",
        "client_email": "firebase-adminsdk-efv01@sudo-70852.iam.gserviceaccount.com",
        "client_id": "114274654285356877826",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-efv01%40sudo-70852.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    })

    # Initialize the Firebase app
    firebase_admin.initialize_app(cred)
    
# Now you can use Firebase as usual
db = firestore.client()


def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Fetch user data from Firebase
        db = firestore.client()
        user_ref = db.collection('users').where('emailAddress', '==', email).stream()

        user_found = False
        for user in user_ref:
            user_data = user.to_dict()
            user_found = True
            
            # Check if user has role 1
            if user_data.get('role') != 1:
                messages.error(request, "You don't have permission to access admin panel.")
                break
            
            # For role 1 users, verify password (you might want to use proper password hashing)
            if user_data.get('emailAddress') == email and user_data.get('password') == password:
                request.session['admin'] = True
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
                break
        
        if not user_found:
            messages.error(request, 'No user found with this email.')
    
    return render(request, 'login.html')

def admin_logout(request):
    request.session.flush()
    return redirect('login')


from datetime import datetime, timedelta
import pytz

def dashboard(request):
    if not request.session.get('admin'):
        return redirect('login')

    ADMIN_EMAIL = "w@w.com"
    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    week_ago = today - timedelta(days=7)
    
    # Users data
    users_ref = db.collection('users')
    users = [
        doc for doc in users_ref.stream()
        if doc.to_dict().get('emailAddress') != ADMIN_EMAIL
    ]
    
    # Orders data
    orders_ref = db.collection('orders')
    all_orders = [doc.to_dict() for doc in orders_ref.stream()]
    
    # Filter orders by date and status
    today_orders = []
    week_orders = []
    status_counts = {status: 0 for status in STATUS_MAPPING.keys()}
    
    for order in all_orders:
        order_date = order.get('timestamp')
        if hasattr(order_date, 'date'):
            order_date = order_date.date()
        elif isinstance(order_date, str):
            order_date = datetime.strptime(order_date, "%B %d, %Y at %I:%M:%S %p UTC%z").date()
        
        status = order.get('orderStatus', 0)
        status_counts[status] = status_counts.get(status, 0) + 1
        
        if order_date == today:
            today_orders.append(order)
        if order_date >= week_ago:
            week_orders.append(order)
    
    # Payment data
    total_earnings = sum(order.get('amount', 0) for order in all_orders if order.get('paymentStatus') == 'paid')
    today_earnings = sum(order.get('amount', 0) for order in today_orders if order.get('paymentStatus') == 'paid')
    
    # QR Codes data
    qr_ref = db.collection('qrcodes')
    all_qr = [doc.to_dict() for doc in qr_ref.stream()]
    active_qr = sum(1 for qr in all_qr if qr.get('isAssigned', False))
    
    context = {
        'total_users': len(users),
        'total_orders': len(all_orders),
        'today_orders': len(today_orders),
        'week_orders': len(week_orders),
        'status_counts': status_counts,
        'total_earnings': total_earnings,
        'today_earnings': today_earnings,
        'total_qr': len(all_qr),
        'active_qr': active_qr,
        'inactive_qr': len(all_qr) - active_qr,
        'STATUS_MAPPING': STATUS_MAPPING,
    }
    return render(request, 'dashboard.html', context)

from django.shortcuts import render, redirect
from io import BytesIO
import qrcode
import base64
import uuid
import datetime
from django.http import HttpResponse
from PIL import Image as PILImage, ImageDraw, ImageFont
import os
from django.conf import settings

def get_font(font_size=20):
    """Helper function to get a font with fallback options"""
    try:
        # Try built-in default font first
        try:
            return ImageFont.truetype("arial.ttf", font_size)
        except:
            # Try common system font paths
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "/Library/Fonts/Arial.ttf",  # macOS
                "C:/Windows/Fonts/arial.ttf",  # Windows
                os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf'),
                os.path.join(settings.BASE_DIR, 'sudo_admin', 'static', 'fonts', 'arial.ttf')
            ]
            
            for path in font_paths:
                if os.path.exists(path):
                    return ImageFont.truetype(path, font_size)
            
            # Final fallback to default font
            return ImageFont.load_default()
    except Exception as e:
        print(f"Font loading error: {str(e)}")
        return ImageFont.load_default()

def generate_qr(request):
    if not request.session.get('admin'):
        return redirect('login')
    
    if request.method == 'POST':
        qr_type = request.POST.get('qr_type', 'user')
        qr_data = []
        base_domain = settings.BASE_DOMAIN
        
        if qr_type == 'user':
            count = int(request.POST.get('count', 1))
            
            for _ in range(count):
                try:
                    # Generate unique IDs
                    qr_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:16]
                    
                    # Create yellow QR code on black background
                    qr = qrcode.QRCode(
                        version=3,  # Increased version for larger capacity
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=12,  # Larger box size for bigger QR code
                        border=2,  # Smaller border to maximize QR code area
                    )
                    qr.add_data(f"{base_domain}/send-notification/{qr_id}/")
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="#dcbd1f", back_color="#161416")

                    # Open template image
                    template_path = os.path.join(settings.BASE_DIR, 'sudo_admin', 'static', 'images', 'qr_template.jpg')
                    if not os.path.exists(template_path):
                        return render(request, 'generate_qr.html', {
                            'error': f'Template image not found at: {template_path}'
                        })

                    template_img = PILImage.open(template_path).convert('RGB')
                    template_width, template_height = template_img.size

                    # Calculate QR code size to occupy 75% of template height
                    qr_size = (int(template_height * 0.75), int(template_height * 0.75))

                    # Position QR code on left side with precise margins
                    left_margin = int(template_width * 0.07)  # 5% from left edge
                    qr_position = (
                        left_margin,  # Left aligned with margin
                        (template_height - qr_size[1]) // 2  # Perfect vertical center
                    )

                    # High-quality resize and paste
                    qr_img = qr_img.resize(qr_size, PILImage.Resampling.LANCZOS)
                    final_img = template_img.copy()
                    final_img.paste(qr_img, qr_position)

                    # Save to buffer
                    buffer = BytesIO()
                    final_img.save(buffer, format="PNG")
                    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    # Save to Firestore
                    qr_data_firestore = {
                        'createdBy': 'admin',
                        'createdDateTime': datetime.datetime.now(tz=datetime.timezone.utc),
                        'isAssigned': False,
                        'qrId': qr_id,
                        'vehicleID': '',
                        'userID': ''
                    }
                    
                    db.collection('qrcodes').document(qr_id).set(qr_data_firestore)
                    
                    qr_data.append({
                        'type': 'user',
                        'qrId': qr_id,
                        'vehicleID': '',
                        'qr_code_base64': qr_code_base64
                    })
                    
                except Exception as e:
                    return render(request, 'generate_qr.html', {
                        'error': f'Failed to generate QR: {str(e)}'
                    })
        else:
            # External QR generation
            count = int(request.POST.get('external_count', 1))
            registration_url = f"{base_domain}/register-external-user/"
            
            for _ in range(count):
                try:
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(registration_url)
                    qr.make(fit=True)
                    qr_img = qr.make_image(fill_color="black", back_color="white")
                    
                    buffer = BytesIO()
                    qr_img.save(buffer, format="PNG")
                    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    qr_data.append({
                        'type': 'external',
                        'qr_code_base64': qr_code_base64
                    })
                except Exception as e:
                    return render(request, 'generate_qr.html', {
                        'error': f'Failed to generate external QR: {str(e)}'
                    })

        request.session['qr_data'] = qr_data
        return render(request, 'generate_qr.html', {'qr_data': qr_data})

    return render(request, 'generate_qr.html')

def download_qr_pdf(request):
    if not request.session.get('admin') or 'qr_data' not in request.session:
        return redirect('login')

    qr_data = request.session.get('qr_data', [])
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr_codes.pdf"'

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import io
    import pytz

    buffer = io.BytesIO()
    # Set minimal margins for maximum width
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          leftMargin=0.3*inch,  # Reduced margins
                          rightMargin=0.3*inch,
                          topMargin=0.4*inch,
                          bottomMargin=0.4*inch)
    elements = []

    # Custom styles
    title_style = ParagraphStyle(
        name="Title",
        fontSize=14,
        alignment=1,  # CENTER
        fontName="Helvetica-Bold",
        spaceAfter=4,
        textColor=colors.black
    )
    
    date_style = ParagraphStyle(
        name="Date",
        fontSize=10,
        alignment=1,  # CENTER
        fontName="Helvetica",
        spaceAfter=12,
        textColor=colors.darkgrey
    )
    
    qr_id_style = ParagraphStyle(
        name="QR_ID",
        fontSize=12,
        alignment=1,  # CENTER
        fontName="Helvetica-Bold",
        spaceBefore=12,  # Increased padding above ID
        textColor=colors.black
    )

    # Title and date (only on first page)
    elements.append(Paragraph("Generated QR Codes", title_style))
    ist = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.datetime.now(ist)
    date_time_string = current_datetime.strftime("%A, %B %d, %Y - %I:%M %p")
    elements.append(Paragraph(f"Created on: {date_time_string}", date_style))
    elements.append(Spacer(1, 24))

    # Calculate maximum possible width (90% of available space)
    page_width = letter[0] - doc.leftMargin - doc.rightMargin
    qr_width = min(4.0*inch, page_width * 0.9)  # Wider format (max 4 inches)
    qr_height = qr_width * 0.5  # Maintain aspect ratio (2:1 width:height)
    items_per_page = 3  # 3 QR codes per page

    for i, qr in enumerate(qr_data):
        if i > 0 and i % items_per_page == 0:
            elements.append(PageBreak())
            # Reset margins for new page
            doc.leftMargin = 0.3*inch
            doc.rightMargin = 0.3*inch

        # Create extra wide QR code image
        qr_img = Image(BytesIO(base64.b64decode(qr['qr_code_base64'])),
                      width=qr_width, height=qr_height)
        
        # Create ID text with padding
        qr_id = Paragraph(qr.get('qrId', ''), qr_id_style)
        
        # Create content with proper spacing
        content_table = Table([
            [qr_img],
            [Spacer(1, 8)],  # Additional padding
            [qr_id]
        ], colWidths=qr_width)
        
        content_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        
        elements.append(content_table)
        elements.append(Spacer(1, 24))  # Space between QR sets

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def register_user(request):
    if not request.session.get('admin'):
        return redirect('login')
    users = db.collection('users').stream()
    user_list = [{'userId': user.id, **user.to_dict()} for user in users]
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        updated_data = {
            'firstname': request.POST.get('firstname'),
            'lastName': request.POST.get('lastname'),
            'emailAddress': request.POST.get('email'),
            'mobileNumber': request.POST.get('mobile'),
            'location': request.POST.get('location'),
        }
        db.collection('users').document(user_id).update(updated_data)
        messages.success(request, 'User updated successfully')
    return render(request, 'register_user.html', {'users': user_list})


def manage_users(request):
    if not request.session.get('admin'):
        messages.error(request, 'Admin access required')
        return redirect('login')

    db = firestore.client()
    ADMIN_EMAIL = "w@w.com"
    
    try:
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        users = []
        for doc in docs:
            user_data = doc.to_dict() or {}
            if user_data.get('emailAddress') == ADMIN_EMAIL:
                continue
                
            user_data['doc_id'] = doc.id
            users.append(user_data)
            
        if not users:
            messages.info(request, 'No users found in database')

    except Exception as e:
        messages.error(request, f'Error accessing database: {str(e)}')
        users = []

    if request.method == "POST":
        if 'delete_selected' in request.POST:
            return handle_bulk_delete(request, users_ref)
        elif 'delete_single' in request.POST:
            user_id = request.POST.get('user_id')
            user_doc = users_ref.document(user_id).get()
            if user_doc.exists and user_doc.to_dict().get('emailAddress') == ADMIN_EMAIL:
                messages.error(request, 'Cannot delete admin account')
                return redirect('manage_users')
            return handle_single_delete(request, users_ref)
        elif 'toggle_status' in request.POST:
            user_id = request.POST.get('user_id')
            user_ref = users_ref.document(user_id)
            user_ref.update({'enabled': not user_ref.get().to_dict().get('enabled', False)})
            messages.success(request, 'User status updated')
            return redirect('manage_users')
        elif 'update_user' in request.POST:
            user_id = request.POST.get('user_id')
            users_ref.document(user_id).update({
                'fullName': request.POST.get('fullName'),
                'city': request.POST.get('city')
            })
            messages.success(request, 'User updated successfully')
            return redirect('manage_users')

    return render(request, 'manage_users.html', {
        'users': users,
        'messages': get_message_list(request)
    })

def handle_bulk_delete(request, users_ref):
    selected_user_ids = request.POST.getlist('selected_users')
    
    if not selected_user_ids:
        messages.warning(request, 'No users selected for deletion')
        return redirect('manage_users')
    
    success_count = 0
    for user_id in selected_user_ids:
        try:
            users_ref.document(user_id).delete()
            success_count += 1
        except Exception as e:
            messages.error(request, f'Error deleting user {user_id}: {str(e)}')
    
    if success_count > 0:
        msg = f'Successfully deleted {success_count} user(s)'
        if success_count != len(selected_user_ids):
            msg += f' (failed to delete {len(selected_user_ids) - success_count})'
        messages.success(request, msg)
    else:
        messages.error(request, 'Failed to delete all selected users')
    
    return redirect('manage_users')


def handle_single_delete(request, users_ref):
    user_id = request.POST.get('user_id')
    
    if not user_id:
        messages.warning(request, 'No user selected for deletion')
        return redirect('manage_users')
    
    try:
        users_ref.document(user_id).delete()
        messages.success(request, 'User deleted successfully')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
    
    return redirect('manage_users')


def get_message_list(request):
    return [{
        'text': message.message,
        'class': message.tags
    } for message in messages.get_messages(request)]


def generate_random_password(length=7):
    """Generate a random password"""
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choice(chars) for _ in range(length))

def check_id_enabled(request, qr_id):
    try:
        # Check if QR code exists and is assigned
        qr_ref = db.collection('qrcodes').document(qr_id)
        qr_doc = qr_ref.get()
        
        if not qr_doc.exists:
            return render(request, 'invalid_qr.html', {'error': 'Invalid QR Code'})
        
        qr_data = qr_doc.to_dict()
        
        if qr_data.get('isAssigned', False):
            # Get the associated vehicle
            vehicle_ref = db.collection('vehicles').document(qr_data['vehicleID'])
            vehicle_doc = vehicle_ref.get()
            
            if vehicle_doc.exists:
                vehicle_data = vehicle_doc.to_dict()
                # Get the user data
                user_ref = db.collection('users').document(vehicle_data['ownerId'])
                user_doc = user_ref.get()
                
                if user_doc.exists and user_doc.to_dict().get('enableIdCheck', False):
                    return redirect('send_notification', qr_id=qr_id)
            
        # If QR not assigned or user not enabled, redirect to activation
        return redirect('activate_id', qr_id=qr_id)
            
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

def send_welcome_email_for_id(email, name, password):
    subject = 'Welcome to Sudo - Your Account is Ready!'
    
    html_message = render_to_string('welcome_email_register.html', {
        'name': name,
        'email': email,
        'password': password,
        'login_url': 'https://play.google.com/',
        'support_email': 'support@sudo.com'
    })
    
    plain_message = f"""
    Welcome to Sudo, {name}!
    
    Your account has been successfully created. Here are your login details:
    
    Email: {email}
    Password: {password}
    
    Please login at: https://play.google.com
    
    We recommend changing your password after first login.
    
    If you have any questions, please contact our support team at support@sudo.com.
    
    Thank you,
    The Sudo Team
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

def send_vehicle_registration_email(email, name, vehicle_data):
    subject = 'Your Vehicle Registration is Complete!'
    
    html_message = render_to_string('vehicle_registration.html', {
        'name': name,
        'email': email,
        'make': vehicle_data['make'],
        'model': vehicle_data['model'],
        'registrationNumber': vehicle_data['registrationNumber'],
        'vehicleType': vehicle_data['vehicleType'],
        'support_email': 'support@sudo.com'
    })
    
    plain_message = f"""
    Hello {name},
    
    Your vehicle has been successfully registered with Sudo:
    
    Make: {vehicle_data['make']}
    Model: {vehicle_data['model']}
    Registration: {vehicle_data['registrationNumber']}
    Type: {vehicle_data['vehicleType']}
    
    Your QR code is now active and can be scanned by others to contact you about your vehicle.
    
    If you have any questions, please contact our support team at support@sudo.com.
    
    Thank you,
    The Sudo Team
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )

@ensure_csrf_cookie
def activate_id(request, qr_id):
    try:
        # Verify QR code exists first
        qr_ref = db.collection('qrcodes').document(qr_id)
        qr_doc = qr_ref.get()
        
        if not qr_doc.exists:
            return render(request, 'invalid_qr.html', {'error': 'Invalid QR Code'})
        
        qr_data = qr_doc.to_dict()
        
        if qr_data.get('isAssigned', False):
            return redirect('send_notification', qr_id=qr_id)
        
        if request.method == 'POST':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                import json
                data = json.loads(request.body)
                
                # Validate required fields
                required_fields = {
                    'user': ['fullName', 'contactNumber', 'city', 'emailAddress'],
                    'vehicle': ['make', 'model', 'registrationNumber', 'vehicleType']
                }
                
                errors = {}
                for field in required_fields['user']:
                    if not data.get(field):
                        errors[field] = 'This field is required'
                
                for field in required_fields['vehicle']:
                    if not data.get(field):
                        errors[field] = 'This field is required'
                
                # Validate email format
                if data.get('emailAddress'):
                    from django.core.validators import validate_email
                    from django.core.exceptions import ValidationError
                    try:
                        validate_email(data['emailAddress'])
                    except ValidationError:
                        errors['emailAddress'] = 'Enter a valid email address'
                
                if errors:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Please correct the errors',
                        'errors': errors
                    }, status=400)
                
                try:
                    # Check if user exists in Firestore
                    user_query = db.collection('users').where('emailAddress', '==', data['emailAddress']).limit(1).get()
                    user_exists_in_firestore = len(user_query) > 0
                    
                    # Check if user exists in Firebase Auth (try to get user)
                    try:
                        auth_user = auth.get_user_by_email(data['emailAddress'])
                        user_exists_in_auth = True
                    except:
                        user_exists_in_auth = False
                    
                    # Handle different cases
                    if user_exists_in_auth and user_exists_in_firestore:
                        # Existing user - proceed with vehicle registration
                        user_doc = user_query[0]
                        user_data = user_doc.to_dict()
                        user_id = user_doc.id
                        
                        # Verify phone matches existing user
                        if user_data.get('contactNumber', '').replace(' ', '') != data['contactNumber'].replace(' ', ''):
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Phone number does not match existing account',
                                'errors': {'contactNumber': 'This phone number does not match your existing account'}
                            }, status=400)

                            
                    elif user_exists_in_auth and not user_exists_in_firestore:
                        # Edge case: user in auth but not in firestore - shouldn't happen
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Account exists but data is incomplete. Please contact support.',
                            'errors': {'emailAddress': 'Account issue detected'}
                        }, status=400)
                        
                    elif not user_exists_in_auth and user_exists_in_firestore:
                        # Edge case: user in firestore but not auth - shouldn't happen
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Account data mismatch. Please contact support.',
                            'errors': {'emailAddress': 'Account issue detected'}
                        }, status=400)
                        
                    else:
                        # New user - create account
                        password = generate_random_password()
                        
                        try:
                            user = auth.create_user(
                                email=data['emailAddress'],
                                email_verified=False,
                                password=password,
                                display_name=data['fullName'],
                                disabled=False
                            )
                        except auth.EmailAlreadyExistsError:
                            # Handle case where user was created between our check and creation attempt
                            user = auth.get_user_by_email(data['emailAddress'])
                            
                        # Create user data in Firestore
                        user_data = {
                            'uid': user.uid,
                            'fullName': data.get('fullName'),
                            'contactNumber': data.get('contactNumber'),
                            'city': data.get('city'),
                            'emailAddress': data.get('emailAddress'),
                            'enableIdCheck': True,
                            'createdAt': firestore.SERVER_TIMESTAMP,
                            'profilePicture': 'default_profile.png',
                            'role': 0
                        }
                        
                        user_ref = db.collection('users').document(user.uid)
                        user_ref.set(user_data)
                        user_id = user.uid
                        
                        # Send welcome email only for new users
                        send_welcome_email_for_id(
                            email=data['emailAddress'],
                            name=data['fullName'],
                            password=password
                        )
                    
                    # Check if this vehicle is already registered to this user
                    vehicle_query = db.collection('vehicles').where('ownerId', '==', user_id)\
                        .where('registrationNumber', '==', data['registrationNumber']).limit(1).get()
                    
                    if len(vehicle_query) > 0:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'This vehicle is already registered to your account',
                            'errors': {'registrationNumber': 'This vehicle is already registered'}
                        }, status=400)
                    
                    # Create vehicle document (for both new and existing users)
                    vehicle_id = str(uuid.uuid4())
                    vehicle_data = {
                        'ownerId': user_id,
                        'ownerFullName': data.get('fullName'),
                        'ownerContact': data.get('contactNumber'),
                        'make': data.get('make'),
                        'model': data.get('model'),
                        'registrationNumber': data.get('registrationNumber'),
                        'vehicleType': data.get('vehicleType'),
                        'createdAt': firestore.SERVER_TIMESTAMP,
                        'isQrGenerated': True,
                        'qrCodeId': qr_id
                    }
                    
                    vehicle_ref = db.collection('vehicles').document(vehicle_id)
                    vehicle_ref.set(vehicle_data)
                    
                    # Update QR code to mark as assigned
                    qr_ref.update({
                        'isAssigned': True,
                        'vehicleID': vehicle_id,
                        'userID': user_id,
                        'assignedAt': firestore.SERVER_TIMESTAMP
                    })
                    
                    # Send vehicle registration email
                    send_vehicle_registration_email(
                        email=data['emailAddress'],
                        name=data['fullName'],
                        vehicle_data=vehicle_data
                    )
                    
                    return JsonResponse({
                        'status': 'success', 
                        'message': 'Vehicle registration completed successfully!',
                        'redirect_url': reverse('send_notification', args=[qr_id]),
                        'is_new_user': not user_exists_in_auth
                    })
                    
                except Exception as e:
                    # Clean up Firebase Auth user if creation failed
                    if 'user' in locals() and user and not user_exists_in_auth:
                        try:
                            auth.delete_user(user.uid)
                        except:
                            pass
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Registration failed: {str(e)}'
                    }, status=500)
        
        # Render the registration form
        context = {
            'is_new_registration': True
        }
        
        return render(request, 'activate_id.html', context)
    
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from firebase_admin import firestore, messaging
from twilio.rest import Client
from django.conf import settings

@ensure_csrf_cookie
def send_notification(request, qr_id):
    try:
        # Get QR code data
        qr_ref = db.collection('qrcodes').document(qr_id)
        qr_doc = qr_ref.get()

        if not qr_doc.exists or not qr_doc.to_dict().get('isAssigned', False):
            return render(request, 'error.html', {'error': 'QR code not assigned!'})

        qr_data = qr_doc.to_dict()
        
        # Get vehicle data
        vehicle_ref = db.collection('vehicles').document(qr_data['vehicleID'])
        vehicle_doc = vehicle_ref.get()
        
        if not vehicle_doc.exists:
            return render(request, 'error.html', {'error': 'Vehicle not found!'})

        vehicle_data = vehicle_doc.to_dict()
        
        # Get user data
        user_ref = db.collection('users').document(vehicle_data['ownerId'])
        user_doc = user_ref.get()
        
        if not user_doc.exists or not user_doc.to_dict().get('enableIdCheck', False):
            return redirect('activate_id', qr_id=qr_id)
        
        user_data = user_doc.to_dict()
        
        if request.method == 'POST':
            # Handle AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                import json
                data = json.loads(request.body)
                
                reason = data.get('reason')
                plate_digits = data.get('plate_digits')
                user_phone = data.get('user_phone', '')
                notification_method = data.get('notification_method', 'push')
                
                # Validate plate digits
                # if plate_digits != vehicle_data.get('registrationNumber', '')[-4:]:
                #     return JsonResponse({
                #         'status': 'error', 
                #         'message': 'The plate number does not match. Please check you are entering the right plate number.'
                #     })
                
                # Handle different notification methods
                if notification_method == 'push':
                    # Existing push notification code
                    fcm_token = user_data.get('fcmToken')
                    
                    if not fcm_token:
                        return JsonResponse({
                            'status': 'error', 
                            'message': 'User does not have a valid FCM token.'
                        })

                    message = messaging.Message(
                        notification=messaging.Notification(
                            title="Vehicle Alert",
                            body=reason,
                        ),
                        token=fcm_token,
                        data={
                            'vehicleId': qr_data['vehicleID'],
                            'qrId': qr_id,
                            'notificationType': 'vehicle_alert'
                        }
                    )

                    try:
                        response = messaging.send(message)
                        return JsonResponse({
                            'status': 'success', 
                            'message': 'We have sent your message to the vehicle owner.'
                        })
                    except Exception as e:
                        return JsonResponse({
                            'status': 'error', 
                            'message': f'Failed to send notification: {str(e)}'
                        })
                
                elif notification_method in ['call', 'sms']:
                    try:
                        # Initialize Twilio client
                        twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                        owner_phone = user_data.get('contactNumber', '')
                        
                        if not owner_phone:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Owner does not have a valid phone number registered.'
                            })
                        
                        if notification_method == 'sms':
                            # Send SMS
                            message = twilio_client.messages.create(
                                body=f"Vehicle Alert: {reason}\n\nFrom: {user_phone or 'Anonymous'}",
                                from_=settings.TWILIO_PHONE_NUMBER,
                                to=owner_phone
                            )
                            return JsonResponse({
                                'status': 'success',
                                'message': 'SMS sent successfully to the vehicle owner.'
                            })
                        
                        elif notification_method == 'call':
                            # Make phone call
                            call = twilio_client.calls.create(
                                twiml=f'<Response><Say>Hello, this is an important message about your vehicle. {reason}. The person trying to reach you provided this number: {user_phone or "not provided"}. Thank you from Sudo.</Say></Response>',
                                from_=settings.TWILIO_PHONE_NUMBER,
                                to=owner_phone
                            )
                            return JsonResponse({
                                'status': 'success',
                                'message': 'Phone call initiated successfully to the vehicle owner.'
                            })
                    
                    except Exception as e:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Failed to send {notification_method}: {str(e)}'
                        })

        # Render the initial page with vehicle data
        context = {
            'vehicle_data': {
                'model': vehicle_data.get('model', ''),
                'registrationNumber': vehicle_data.get('registrationNumber', '')
            }
        }
        
        return render(request, 'send_notification.html', context)
    
    except Exception as e:
        return render(request, 'error.html', {'error': str(e)})

# Define status mapping
STATUS_MAPPING = {
    0: "Pending",
    1: "Processing",
    2: "Shipped",
    3: "Delivered",
    4: "Cancelled",
    5: "Returned",
    6: "Failed",
    7: "On Hold",
}

def view_orders(request):
    try:
        # Fetch orders from the 'orders' collection
        orders_ref = db.collection('orders')
        orders = orders_ref.stream()

        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            order_dict['id'] = order.id  # Add the document ID to the order data
            
            # Map order status to its corresponding text
            order_status = order_dict.get('orderStatus', 0)
            order_dict['status_text'] = STATUS_MAPPING.get(order_status, "Unknown")

            orders_data.append({
                'order': order_dict,
            })

        context = {
            'orders': orders_data,
            'STATUS_MAPPING': STATUS_MAPPING,
        }
        return render(request, 'view_orders.html', context)

    except Exception as e:
        return render(request, 'view_orders.html', {'error': str(e)})
    
def update_order_status(request):
    if request.method == 'POST':
        try:
            order_id = request.POST.get('orderId')
            new_status = int(request.POST.get('newStatus'))

            if not order_id:
                return JsonResponse({'success': False, 'error': 'Order ID is required'})

            # Update ONLY the order status in the database
            order_ref = db.collection('orders').document(order_id)
            order_ref.update({
                'orderStatus': new_status,
                'status_text': STATUS_MAPPING.get(new_status, "Unknown")
            })

            return JsonResponse({
                'success': True,
                'status_text': STATUS_MAPPING.get(new_status, "Unknown")
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def external_user_registration(request):
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('fullName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        city = request.POST.get('city')
        
        # Generate user ID and random password
        user_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:8]
        temp_password = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:12]
        
        try:
            # Create Firebase Authentication user
            user = auth.create_user(
                email=email,
                email_verified=False,
                password=temp_password,
                display_name=full_name,
                disabled=False
            )
            
            # Create user data for Firestore
            user_data = {
                'userId': user_id,
                'fullName': full_name,
                'emailAddress': email,
                'contactNumber': phone,
                'city': city,
                'createdAt': datetime.datetime.now(),
                'role': 0,  # Regular user role
                'profilePicture': 'default_profile.png',
                'fcmToken': '',  # Will be set when user installs the app
                'enableIdCheck': False
            }
            
            # Save to Firestore
            db.collection('users').document(user_id).set(user_data)
            
            # Send welcome email with credentials
            send_welcome_email(email, full_name, temp_password)
            
            # Success - redirect to thank you page
            return render(request, 'registration_success.html')
            
        except Exception as e:
            # Error handling
            return render(request, 'external_register.html', {
                'error': f'Registration failed: {str(e)}',
                'form_data': request.POST
            })
    
    # GET request - show empty form
    return render(request, 'external_register.html')

def send_welcome_email(email, name, password):
    subject = 'Welcome to Sudo - Your Account Details'
    
    # Render HTML email template
    html_message = render_to_string('welcome_email.html', {
        'name': name,
        'email': email,
        'password': password,
        'login_url': 'https://play.google.com/',
        'support_email': 'support@sudo.com'
    })
    
    # Plain text version
    plain_message = f"""
    Welcome to Sudo, {name}!
    
    Your account has been successfully created. Here are your login details:
    
    Email: {email}
    Temporary Password: {password}
    
    Please login at: https://play.google.com/
    
    We recommend changing your password after first login.
    
    If you have any questions, please contact our support team at support@sudo.com.
    
    Thank you,
    The Sudo Team
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )


@csrf_exempt
def send_feedback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Prepare email content
            context = {
                'name': data.get('name', 'User'),
                'email': data.get('email', ''),
                'vehicle': data.get('vehicle', ''),
                'rating': data.get('rating', 0),
                'feedback': data.get('feedback', 'No feedback provided'),
            }
            
            # Render email templates
            subject = f"New Feedback Received - Rating: {context['rating']}/5"
            text_content = render_to_string('feedback_email.txt', context)
            html_content = render_to_string('feedback_email.html', context)
            
            # Send email to admin
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [settings.FEEDBACK_EMAIL],
                html_message=html_content,
                fail_silently=False,
            )
            
            # Send confirmation to user
            if context['email']:
                user_subject = "Thank You for Your Feedback"
                user_text = render_to_string('feedback_user_email.txt', context)
                user_html = render_to_string('feedback_user_email.html', context)
                
                send_mail(
                    user_subject,
                    user_text,
                    settings.DEFAULT_FROM_EMAIL,
                    [context['email']],
                    html_message=user_html,
                    fail_silently=False,
                )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def send_feedback_notify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Prepare email content
            context = {
                'contact_reason': data.get('contact_reason', 'Not specified'),
                'feedback': data.get('feedback', 'No feedback provided'),
                'rating': data.get('rating', 0),
                'vehicle_model': data.get('vehicle_model', 'Unknown vehicle'),
                'notification_method': data.get('notification_method', 'push')
            }
            
            # Render email templates
            subject = f"New Feedback Received - Rating: {context['rating']}/5"
            text_content = render_to_string('feedback_email_notify.txt', context)
            html_content = render_to_string('feedback_email_notify.html', context)
            
            # Send email to admin
            send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [settings.FEEDBACK_EMAIL],
                html_message=html_content,
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def manage_qrs(request):
    if not request.session.get('admin'):
        messages.error(request, 'Admin access required')
        return redirect('login')

    db = firestore.client()
    
    try:
        qrs_ref = db.collection('qrcodes')
        query = qrs_ref
        
        # Handle filters
        status_filter = request.GET.get('status')
        search_query = request.GET.get('search')
        
        if status_filter == 'active':
            query = query.where('isAssigned', '==', True)
        elif status_filter == 'inactive':
            query = query.where('isAssigned', '==', False)
        
        qr_docs = query.stream()
        
        # Prepare QR data with additional user/vehicle info
        qrs = []
        user_cache = {}
        vehicle_cache = {}
        
        for doc in qr_docs:
            qr_data = doc.to_dict() or {}
            qr_data['doc_id'] = doc.id
            
            # Generate QR code image for each QR
            qr = qrcode.QRCode(
                version=3,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=4,
                border=2,
            )
            qr.add_data(f"{settings.BASE_DOMAIN}/send-notification/{doc.id}/")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="#dcbd1f", back_color="#161416")
            
            # Convert to base64
            buffer = BytesIO()
            qr_img.save(buffer, format="PNG")
            qr_data['qr_code_base64'] = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            # Add user info if assigned
            if qr_data.get('isAssigned') and qr_data.get('userID'):
                if qr_data['userID'] not in user_cache:
                    try:
                        user_doc = db.collection('users').document(qr_data['userID']).get()
                        user_cache[qr_data['userID']] = user_doc.to_dict() if user_doc.exists else None
                    except:
                        user_cache[qr_data['userID']] = None
                
                qr_data['user'] = user_cache[qr_data['userID']]
            
            # Add vehicle info if assigned
            if qr_data.get('isAssigned') and qr_data.get('vehicleID'):
                if qr_data['vehicleID'] not in vehicle_cache:
                    try:
                        vehicle_doc = db.collection('vehicles').document(qr_data['vehicleID']).get()
                        vehicle_cache[qr_data['vehicleID']] = vehicle_doc.to_dict() if vehicle_doc.exists else None
                    except:
                        vehicle_cache[qr_data['vehicleID']] = None
                
                qr_data['vehicle'] = vehicle_cache[qr_data['vehicleID']]
            
            # Apply search filter if provided
            if search_query:
                search_lower = search_query.lower()
                matches = False
                
                # Check QR ID
                if search_lower in doc.id.lower():
                    matches = True
                
                # Check user info
                if not matches and qr_data.get('user'):
                    user = qr_data['user']
                    if (search_lower in user.get('fullName', '').lower() or 
                        search_lower in user.get('emailAddress', '').lower() or 
                        search_lower in user.get('contactNumber', '').lower()):
                        matches = True
                
                # Check vehicle info
                if not matches and qr_data.get('vehicle'):
                    vehicle = qr_data['vehicle']
                    if (search_lower in vehicle.get('ownerFullName', '').lower() or 
                        search_lower in vehicle.get('registrationNumber', '').lower() or 
                        search_lower in vehicle.get('make', '').lower() or 
                        search_lower in vehicle.get('model', '').lower()):
                        matches = True
                
                if not matches:
                    continue
            
            qrs.append(qr_data)
            
        if not qrs:
            messages.info(request, 'No QR codes found matching your criteria')

    except Exception as e:
        messages.error(request, f'Error accessing database: {str(e)}')
        qrs = []

    # Handle export request
    if request.GET.get('export') == 'pdf':
        return export_qrs_pdf(request, qrs)
    
    return render(request, 'manage_qrs.html', {
        'qrs': qrs,
        'status_filter': status_filter,
        'search_query': search_query,
        'messages': get_message_list(request)
    })

def export_qrs_pdf(request, qrs):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qr_codes_export.pdf"'

    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    import pytz

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          leftMargin=0.5*inch,
                          rightMargin=0.5*inch,
                          topMargin=0.5*inch,
                          bottomMargin=0.5*inch)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="Title",
        fontSize=14,
        alignment=1,  # CENTER
        fontName="Helvetica-Bold",
        spaceAfter=12,
        textColor=colors.black
    )
    
    date_style = ParagraphStyle(
        name="Date",
        fontSize=10,
        alignment=1,  # CENTER
        fontName="Helvetica",
        spaceAfter=6,
        textColor=colors.darkgrey
    )
    
    # Title and date
    elements.append(Paragraph("QR Codes Export", title_style))
    ist = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.datetime.now(ist)
    date_str = current_datetime.strftime("%B %d, %Y at %I:%M %p")
    elements.append(Paragraph(f"Generated on: {date_str}", date_style))
    
    if request.GET.get('status'):
        elements.append(Paragraph(f"Status: {request.GET.get('status').capitalize()}", date_style))
    if request.GET.get('search'):
        elements.append(Paragraph(f"Search: {request.GET.get('search')}", date_style))
    
    elements.append(Spacer(1, 24))

    # QR code display settings
    qr_size = 1.5 * inch
    items_per_row = 3
    items_per_page = items_per_row * 3  # 3 rows per page
    
    for i, qr in enumerate(qrs):
        if i > 0 and i % items_per_page == 0:
            elements.append(PageBreak())
        
        if i % items_per_row == 0:
            # Start new row
            row_data = []
        
        # Create QR image
        qr_img = Image(BytesIO(base64.b64decode(qr['qr_code_base64'])),
                      width=qr_size, height=qr_size)
        
        # Create info text
        info = [
            Paragraph(f"<b>QR ID:</b> {qr['doc_id'][:12]}...", styles['Normal']),
            Paragraph(f"<b>Status:</b> {'Active' if qr.get('isAssigned') else 'Inactive'}", styles['Normal'])
        ]
        
        if qr.get('user'):
            info.append(Paragraph(f"<b>User:</b> {qr['user'].get('fullName', '')}", styles['Normal']))
        
        if qr.get('vehicle'):
            info.append(Paragraph(f"<b>Vehicle:</b> {qr['vehicle'].get('registrationNumber', '')}", styles['Normal']))
        
        # Combine QR and info
        item_table = Table([
            [qr_img],
            info
        ], colWidths=qr_size)
        
        row_data.append(item_table)
        
        if (i + 1) % items_per_row == 0 or i == len(qrs) - 1:
            # Complete the row
            row_table = Table([row_data], colWidths=[qr_size]*len(row_data))
            row_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
            ]))
            elements.append(row_table)
            elements.append(Spacer(1, 12))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def regenerate_qr(request, qr_id):
    if not request.session.get('admin'):
        messages.error(request, 'Admin access required')
        return redirect('login')

    db = firestore.client()
    
    try:
        # Get existing QR code data
        qr_ref = db.collection('qrcodes').document(qr_id)
        qr_doc = qr_ref.get()
        
        if not qr_doc.exists:
            messages.error(request, 'QR code not found')
            return redirect('manage_qrs')
        
        # Generate the same QR code again
        qr = qrcode.QRCode(
            version=3,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
            border=2,
        )
        qr.add_data(f"{settings.BASE_DOMAIN}/send-notification/{qr_id}/")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#dcbd1f", back_color="#161416")

        # Open template image
        template_path = os.path.join(settings.BASE_DIR, 'sudo_admin', 'static', 'images', 'qr_template.jpg')
        if not os.path.exists(template_path):
            messages.error(request, 'Template image not found')
            return redirect('manage_qrs')

        template_img = PILImage.open(template_path).convert('RGB')
        template_width, template_height = template_img.size

        # Calculate QR code size to occupy 75% of template height
        qr_size = (int(template_height * 0.75), int(template_height * 0.75))

        # Position QR code
        left_margin = int(template_width * 0.07)
        qr_position = (
            left_margin,
            (template_height - qr_size[1]) // 2
        )

        # Paste QR code onto template
        qr_img = qr_img.resize(qr_size, PILImage.Resampling.LANCZOS)
        final_img = template_img.copy()
        final_img.paste(qr_img, qr_position)

        # Save to buffer
        buffer = BytesIO()
        final_img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Prepare response
        response = HttpResponse(content_type='image/png')
        response['Content-Disposition'] = f'attachment; filename="qr_{qr_id}.png"'
        response.write(buffer.getvalue())
        buffer.close()
        
        return response

    except Exception as e:
        messages.error(request, f'Error regenerating QR code: {str(e)}')
        return redirect('manage_qrs')
    
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import qrcode
import base64
import pytz
from datetime import datetime

def print_orders(request):
    order_ids = request.GET.get('order_ids', '').split(',')
    if not order_ids:
        return HttpResponse("No orders selected", status=400)
    
    try:
        # Fetch selected orders
        orders = []
        for order_id in order_ids:
            order_ref = db.collection('orders').document(order_id)
            order = order_ref.get().to_dict()
            if order:
                order['id'] = order_id
                orders.append(order)
        
        if not orders:
            return HttpResponse("No orders found", status=404)
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="orders.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              leftMargin=0.5*inch,
                              rightMargin=0.5*inch,
                              topMargin=0.5*inch,
                              bottomMargin=0.5*inch)
        
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceAfter=10
        )
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph("Order Details", title_style))
        
        # Date
        ist = pytz.timezone('Asia/Kolkata')
        current_datetime = datetime.now(ist)
        date_time_string = current_datetime.strftime("%A, %B %d, %Y - %I:%M %p")
        elements.append(Paragraph(f"Generated on: {date_time_string}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Add each order
        for order in orders:
            # Order header
            elements.append(Paragraph(f"Order ID: {order.get('id', '')}", heading_style))
            
            # Customer info
            customer_data = [
                ['Customer Name:', order.get('fullName', '')],
                ['Mobile:', order.get('mobile', '')],
                ['Alternate Mobile:', order.get('mobileNumber', '')],
            ]
            customer_table = Table(customer_data, colWidths=[1.5*inch, 4*inch])
            customer_table.setStyle(TableStyle([
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ]))
            elements.append(customer_table)
            elements.append(Spacer(1, 10))
            
            # Product info
            product_data = [
                ['Product:', order.get('selectedItem', '')],
                ['Quantity:', order.get('quantity', '')],
                ['Amount:', f"₹{order.get('amount', '')}"],
            ]
            product_table = Table(product_data, colWidths=[1.5*inch, 4*inch])
            elements.append(product_table)
            elements.append(Spacer(1, 10))
            
            # Vehicle info
            vehicle_data = [
                ['Vehicle Category:', order.get('vehicleCategory', '')],
                ['Vehicle Number:', order.get('vehicleNumber', '')],
            ]
            vehicle_table = Table(vehicle_data, colWidths=[1.5*inch, 4*inch])
            elements.append(vehicle_table)
            elements.append(Spacer(1, 10))
            
            # Address
            address = order.get('address', {})
            address_text = f"{address.get('houseNumber', '')}, {address.get('street', '')}\n"
            address_text += f"{address.get('landmark', '')}\n"
            address_text += f"{address.get('city', '')}, {address.get('state', '')}\n"
            address_text += f"{address.get('pincode', '')}, {address.get('country', '')}"
            
            elements.append(Paragraph("Delivery Address:", normal_style))
            elements.append(Paragraph(address_text, normal_style))
            elements.append(Spacer(1, 10))
            
            # Payment and status
            status_data = [
                ['Payment Status:', order.get('paymentStatus', '')],
                ['Order Status:', STATUS_MAPPING.get(order.get('orderStatus', 0), "Unknown")],
                ['Order Date:', order.get('timestamp', '').strftime("%d %b %Y %I:%M %p") if hasattr(order.get('timestamp', ''), 'strftime') else ''],
            ]
            status_table = Table(status_data, colWidths=[1.5*inch, 4*inch])
            elements.append(status_table)
            
            # Add page break if not last order
            if order != orders[-1]:
                elements.append(PageBreak())
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)

def export_orders_with_qr(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)
    
    order_ids = request.POST.getlist('order_ids')
    if not order_ids:
        return HttpResponse("No orders selected", status=400)
    
    try:
        # Fetch selected orders
        orders = []
        for order_id in order_ids:
            order_ref = db.collection('orders').document(order_id)
            order = order_ref.get().to_dict()
            if order:
                order['id'] = order_id
                orders.append(order)
        
        if not orders:
            return HttpResponse("No orders found", status=404)
        
        # Create PDF with QR codes
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="orders_with_qr.pdf"'
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              leftMargin=0.5*inch,
                              rightMargin=0.5*inch,
                              topMargin=0.5*inch,
                              bottomMargin=0.5*inch)
        
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=20
        )
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceAfter=10
        )
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph("Order Details with QR Codes", title_style))
        
        # Date
        ist = pytz.timezone('Asia/Kolkata')
        current_datetime = datetime.now(ist)
        date_time_string = current_datetime.strftime("%A, %B %d, %Y - %I:%M %p")
        elements.append(Paragraph(f"Generated on: {date_time_string}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Add each order with QR code
        for order in orders:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr_data = f"Order ID: {order['id']}\nCustomer: {order.get('fullName', '')}\nProduct: {order.get('selectedItem', '')}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_buffer = BytesIO()
            qr_img.save(qr_buffer, format="PNG")
            qr_buffer.seek(0)
            
            # Create table with order info and QR code
            order_data = [
                [
                    # Order info
                    Table([
                        [Paragraph("Order Details", heading_style)],
                        [Paragraph(f"Order ID: {order.get('id', '')}", normal_style)],
                        [Paragraph(f"Customer: {order.get('fullName', '')}", normal_style)],
                        [Paragraph(f"Product: {order.get('selectedItem', '')}", normal_style)],
                        [Paragraph(f"Quantity: {order.get('quantity', '')}", normal_style)],
                        [Paragraph(f"Amount: ₹{order.get('amount', '')}", normal_style)],
                        [Paragraph(f"Status: {STATUS_MAPPING.get(order.get('orderStatus', 0), 'Unknown')}", normal_style)],
                    ], colWidths=[3.5*inch]),
                    
                    # QR code
                    Image(qr_buffer, width=1.5*inch, height=1.5*inch)
                ]
            ]
            
            order_table = Table(order_data, colWidths=[3.5*inch, 1.5*inch])
            order_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('ALIGN', (1,0), (1,0), 'RIGHT'),
                ('BOX', (0,0), (-1,-1), 1, colors.grey),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ]))
            
            elements.append(order_table)
            elements.append(Spacer(1, 20))
            
            # Add page break if not last order
            if order != orders[-1]:
                elements.append(PageBreak())
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    
    except Exception as e:
        return HttpResponse(f"Error generating PDF: {str(e)}", status=500)