from rest_framework import serializers
from .models import User,Employee,OTP,EmployeeAttendance
from django.core.mail import send_mail
from django.utils.crypto import get_random_string


""" ------------User registration serializers--------------"""
class UserRegisterSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model= User
        fields=['email','name','password','password2']

        extra_kwargs={
            'password':{'write_only':True}
        }

    #-------------------validate password & Confirm Password -----------------
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm password doesn't match.")
        return attrs
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    # super().create(validated_data)

""" ---------------User Login serializers-------------"""
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=100)
    class Meta:
        model=User
        fields=['email','password']

""" ---------------User profile serializers to get all the data about User-------------"""
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields= ['id','email','name']


""" ---------------User password change serializers-------------"""
class UserPasswordChangeSerializer(serializers.Serializer):
    password=serializers.CharField(max_length=12,min_length=6,style={'input_type':'password'},write_only=True)
    password2=serializers.CharField(max_length=12,min_length=6,style={'input_type':'password'},write_only=True)
    class Meta:
        fields=['password','password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user=self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password & Confirm password doesn't match.")
        user.set_password(password)
        user.save()
        return attrs

""" ---------------OTP send User password Forget serializers-------------"""
class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Provided Email is Invalid.")
        return attrs

    def save(self):
        email = self.validated_data['email']
        otp = get_random_string(length=6, allowed_chars='0123456789')
        # Save OTP in the model 
        OTP.objects.create(email=email, otp=otp)
        # Send OTP to user's email
        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is {otp}',
            'daring.dk420@gmail.com',  # Replace with your email
            [email],
            fail_silently=False,)



""" ---------------OTP Validation for User password Forget serializers-------------"""

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6, max_length=8)

    class Meta:
        fields = ['email', 'otp', 'new_password']

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')
        if not OTP.objects.filter(email=email, otp=otp).exists():
            raise serializers.ValidationError("Invalid OTP.")
        return attrs

    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        otp_record = OTP.objects.get(email=email, otp=self.validated_data['otp'])

        # if otp_record.is_valid():
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()

            # Optionally, delete the OTP record after successful validation
        otp_record.delete()
        # else:
        #     raise serializers.ValidationError("OTP has expired.")





""" ----------------New employee Register by admin-------------"""
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['date', 'zone', 'employee_code', 'employee_name', 'department', 'category', 'supervisor_name']



""" -------------------------------- employee Search Serializers----------------------------------"""
class EmployeeSearchSerializer(serializers.Serializer):
    employee_code = serializers.CharField(required=False, max_length=10)
    zone = serializers.CharField(required=False, max_length=100)
    supervisor_name = serializers.CharField(required=False, max_length=100)
    employee_name = serializers.CharField(required=False, max_length=100)
    date = serializers.DateField(required=False)

    class Meta:
        fields = ['employee_code', 'zone', 'supervisor_name', 'employee_name', 'date']






""" -------------------------------- EmployeeAttendance Serializers----------------------------------"""
class EmployeeAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAttendance
        fields = '__all__'

    # Custom validation for 0/1 integer fields if needed
    def validate(self, data):
        fields_to_validate = ['sk', 'sk_ot', 'ssk', 'ssk_ot', 'usk', 'usk_ot']
        for field in fields_to_validate:
            if data[field] not in [0, 1]:
                raise serializers.ValidationError(f'{field} should be either 0 or 1')
        return data