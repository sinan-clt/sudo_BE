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

TWILIO_ACCOUNT_SID = 'ACf0c95d735353e43442a3149a90adfcef'  
TWILIO_AUTH_TOKEN = '0dfe5c52f93d1fe59f9e1e8a406584df'  
TWILIO_PHONE_NUMBER = '+19895205533'   

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
            if user_data.get('role') != 1:
                # Role is not 1, show an access message
                messages.error(request, "You don't have access to login.")
                break
            elif user_data.get('emailAddress') == email and password == '123456': 
                # Role is 1, user is allowed to login
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


def dashboard(request):
    if not request.session.get('admin'):
        return redirect('login')

    users_ref = db.collection('users')
    users = list(users_ref.stream()) 

    context = {
        'total_users': len(users),
        'users': users
    }
    return render(request, 'dashboard.html', context)


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
                    vehicle_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:12]
                    
                    # Create QR code
                    registration_url = f"{base_domain}/send-notification/{qr_id}/"
                    qr_code = qrcode.make(registration_url)
                    buffer = BytesIO()
                    qr_code.save(buffer, format="PNG")
                    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    # Save to Firestore qrcodes collection
                    qr_data_firestore = {
                        'createdBy': 'admin',
                        'createdDateTime': datetime.datetime.now(tz=datetime.timezone.utc),
                        'isAssigned': False,
                        'qrId': qr_id,
                        'vehicleID': '',  # Add vehicleID reference
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
            # External QR generation remains the same
            count = int(request.POST.get('external_count', 1))
            registration_url = f"{base_domain}/register-external-user/"
            
            for _ in range(count):
                try:
                    qr_code = qrcode.make(registration_url)
                    buffer = BytesIO()
                    qr_code.save(buffer, format="PNG")
                    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                    
                    qr_data.append({
                        'type': 'external',
                        'qr_code_base64': qr_code_base64
                    })
                except Exception as e:
                    return render(request, 'generate_qr.html', {
                        'error': f'Failed to generate QR: {str(e)}'
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
    from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    import io
    import pytz

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name="Title",
        fontSize=24,
        alignment=1,
        fontName="Helvetica-Bold",
        spaceAfter=12,
        textColor=colors.black
    )
    date_style = ParagraphStyle(
        name="Date",
        fontSize=12,
        alignment=1,
        fontName="Helvetica",
        spaceBefore=18,
        spaceAfter=24,
        textColor=colors.darkgrey
    )

    title = Paragraph("Generated QR Codes", title_style)
    elements.append(title)
    
    ist = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.datetime.now(ist)
    date_time_string = current_datetime.strftime("%A, %B %d, %Y - %I:%M %p")
    date_time_paragraph = Paragraph(f"Created on: {date_time_string}", date_style)
    elements.append(date_time_paragraph)
    elements.append(Spacer(1, 18))

    data = []
    row = []

    for qr in qr_data:
        # Updated to use qrId instead of userId
        label = f"QR ID: {qr['qrId']}" if qr['type'] == 'user' else "External Registration"
        
        qr_image = Image(BytesIO(base64.b64decode(qr['qr_code_base64'])), width=150, height=150)
        label_paragraph = Paragraph(f"<b>{label}</b>", styles['BodyText'])
        
        if len(row) < 2:
            row.append([qr_image, label_paragraph])
        else:
            data.append(row)
            row = [[qr_image, label_paragraph]]

    if row:
        data.append(row)

    table = Table(data, colWidths=[doc.width/2.2]*2)
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))

    elements.append(table)
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
    # Ensure the user is an admin
    if not request.session.get('admin'):
        messages.error(request, 'Admin access required')
        return redirect('login')

    # Connect to Firestore
    db = firestore.client()
    
    try:
        # Get all documents from the users collection
        users_ref = db.collection('users')
        docs = users_ref.stream()
        
        # Prepare user data with document IDs
        users = []
        for doc in docs:
            user_data = doc.to_dict() or {}
            user_data['doc_id'] = doc.id
            users.append(user_data)
            
        if not users:
            messages.info(request, 'No users found in database')

    except Exception as e:
        messages.error(request, f'Error accessing database: {str(e)}')
        users = []

    # Handle deletion requests
    if request.method == "POST":
        if 'delete_selected' in request.POST:
            return handle_bulk_delete(request, users_ref)
        elif 'delete_single' in request.POST:
            return handle_single_delete(request, users_ref)

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
                if plate_digits != vehicle_data.get('registrationNumber', '')[-4:]:
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'The plate number does not match. Please check you are entering the right plate number.'
                    })
                
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
                        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
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
                                from_=TWILIO_PHONE_NUMBER,
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
                                from_=TWILIO_PHONE_NUMBER,
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