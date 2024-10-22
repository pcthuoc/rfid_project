import csv
import json
import xlwt
import xlrd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser
from django.utils import timezone
from django.utils.encoding import smart_str
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import Student, Log
import base64
from django.core.files.base import ContentFile
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import xlsxwriter
import xlrd
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

global stat
stat = ''
# Create your views here.
global selected
selected = None

@csrf_exempt 
def getid(request):
    # Lấy 'masv' từ request (URL hoặc query parameter)
    masv = request.GET.get('masv')

    if not masv:
        return JsonResponse({'status': 'fail', 'message': 'Mã sinh viên không được cung cấp'})

    # Tìm kiếm sinh viên theo mã sinh viên (masv)
    try:
        user = Student.objects.get(masv=masv)
    except Student.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Không tìm thấy sinh viên'})

    # Trả về ID vân tay và mã sinh viên dưới dạng JSON
    return JsonResponse({'status': 'success', 'fingerid': user.finger_id, 'maSV': user.masv})
def upload_fingerprint(request):
    if request.method == 'POST':
        # Lấy dữ liệu vân tay từ request POST
        fingerprint_data = request.body  # Dữ liệu nhị phân được gửi trực tiếp trong request

        if not fingerprint_data:
            return JsonResponse({'status': 'failed', 'message': 'No fingerprint data received'}, status=400)

        try:
            # Kiểm tra dữ liệu nhận được (in ra kích thước dữ liệu)
            print(f"Received fingerprint data of length: {len(fingerprint_data)} bytes")

            # Bạn có thể lưu dữ liệu hoặc xử lý tùy theo yêu cầu của mình
            # Ví dụ: lưu dữ liệu vân tay vào file
            with open("fingerprint_template.bin", "wb") as f:
                f.write(fingerprint_data)

            # Trả về phản hồi thành công
            return JsonResponse({'status': 'success', 'message': 'Fingerprint uploaded successfully'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'failed', 'message': 'Invalid request method'}, status=405)


def index1(request):
    logs = Log.objects.all().order_by('-date', '-time_in')
    dataset = {'log': logs}
    return render(request, 'attendance/attendance.html', dataset)


def index(request):
    logs = Log.objects.order_by('-date', '-time_in')  # Sắp xếp theo ngày và thời gian check-in mới nhất trước
    return render(request, 'attendance/index.html', {'logs': logs})


def process(request):
    # Lấy finger_id từ query parameter
    finger_id = request.GET.get('finger_id')
    print(finger_id)

    # Kiểm tra nếu finger_id không tồn tại hoặc không hợp lệ
    if not finger_id or not finger_id.isdigit() or int(finger_id) == 0:
        return JsonResponse({'status': 'fail', 'message': 'Invalid or missing finger_id'}, status=400)

    try:
        # Tìm sinh viên theo finger_id
        user = Student.objects.get(finger_id=int(finger_id))
    except Student.DoesNotExist:
        return JsonResponse({'status': 'fail', 'message': 'Student not found'}, status=404)

    # Nếu sinh viên tồn tại, gọi hàm attend để xử lý check-in/check-out
    status, masv = attend(user)

    # Gửi thông báo qua WebSocket (nếu cần)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications',  # Tên group channel
        {
            'type': 'send_notification',
            'message': f'Student {user.name} performed {status}'  # Nội dung thông báo
        }
    )

    # Trả về kết quả dưới dạng JSON
    return JsonResponse({'status': status, 'maSV': masv})

def attend(user):
    # Lấy log gần nhất của sinh viên, sắp xếp theo ngày và thời gian check-in gần nhất
    logs = Log.objects.filter(student=user).order_by('-date', '-time_in')
    current_time = timezone.now()  # Lấy thời gian hiện tại theo múi giờ của Django

    # Nếu không có log hoặc log gần nhất đã check-out, thực hiện check-in
    if not logs.exists() or logs.first().time_out is not None:
        new_log = Log.objects.create(
            student=user,
            date=current_time,  # Lưu ngày hiện tại
            time_in=current_time,  # Lưu thời gian check-in (ngày + giờ theo múi giờ Django)
            status='check_in'
        )
        return 'check_in', user.masv

    # Nếu log gần nhất chưa check-out, thực hiện check-out
    else:
        log = logs.first()
        log.date=current_time
        log.time_out = current_time  # Lưu thời gian check-out (theo múi giờ Django)
        log.status = 'check_out'
        log.save()  # Lưu log đã cập nhật
        return 'check_out', user.masv
def alluser(request):

    sort_by = request.GET.get('sort_by', 'id') 
    order = request.GET.get('order', 'asc')    

    if order == 'desc':
        sort_by = f'-{sort_by}'

    users = Student.objects.all().order_by(sort_by)


    context = {
        'users': users
    }
    html_template = loader.get_template('attendance/allusers.html')  
    return HttpResponse(html_template.render(context, request))  

def manage(request):
    users = Student.objects.all().order_by('id')
    context = {'users': users} 
    return render(request, 'attendance/manage.html', context)

@csrf_exempt  # Bỏ qua kiểm tra CSRF cho API (trong trường hợp gọi từ bên ngoài)
def update_finger_id_via_url(request):
    # Lấy mã sinh viên và finger_id từ query parameters
    masv = request.GET.get('masv')
    finger_id = request.GET.get('fingerid')
    print(masv)
    print(finger_id)


    if not masv or not finger_id:
        return JsonResponse({'status': 'error', 'message': 'Mã sinh viên và Finger ID không được để trống'}, status=400)

    try:
        # Tìm sinh viên theo mã sinh viên
        student = Student.objects.get(masv=masv)
        # Cập nhật finger_id cho sinh viên
        student.finger_id = finger_id
        student.save()

        return JsonResponse({'status': 'success', 'message': 'Finger ID updated successfully'}, status=200)
    except Student.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Student not found'}, status=404)

def card(request):
	sel_user = ''
	users = Student.objects.all().order_by('id')
	global stat
	global selected
	if request.method == 'POST':
		if request.POST.get("sel"):
			ids = request.POST.get('idsearch', 'kuch nahi mila')
			for user in users:
				if user.card_id == int(ids):
					stat = 'Card is Selected'
					selected = user
					break
				else:
					stat = 'Card not found'
			return redirect('/manage')
		else:
			ids = request.POST.get('idsearch')
			if Student.objects.filter(card_id=int(ids)).exists():
				Student.objects.filter(card_id=int(ids)).delete()
				Log.objects.filter(card_id=int(ids)).delete()

				stat = 'Deleted Successfully'
			else:
				stat = 'Card not found'
			return redirect('/manage')

def add(request):
    # Lấy thông tin từ request POST
    name = request.POST.get('name')
    class_name = request.POST.get('class_name')
    masv = request.POST.get('masv')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    sex = request.POST.get('sex')

    
    # Tạo một đối tượng Student mới và lưu vào cơ sở dữ liệu
    new_student = Student(
        name=name,
        class_name=class_name,
        masv=masv,
        phone=phone,
        email=email,
        sex=sex
    )
    new_student.save()
    
    # Chuyển hướng người dùng đến một trang hoặc URL khác sau khi thêm thành công
    return redirect('/manage')
	
def edit_student(request, student_id):
    if request.method == 'POST':
        # Lấy sinh viên theo student_id từ URL
        student = get_object_or_404(Student, id=student_id)
        
        # Cập nhật các trường thông tin từ request POST
        student.name = request.POST.get('name')
        student.class_name = request.POST.get('class_name')
        student.masv = request.POST.get('masv')
        student.phone = request.POST.get('phone')
        student.email = request.POST.get('email')
        student.sex = request.POST.get('sex')
        
        student.save()  # Lưu các thay đổi vào database
        
        return redirect('/manage')  # Chuyển hướng về trang quản lý sinh viên
def search(request):
	sel_user = ''
	users = Student.objects.all()
	logs = Log.objects.all()
	path = request.get_full_path()
	card_id = request.POST.get('search').strip() if request.POST.get('search') else None

	logf = []
	for user in users:
		if str(user.card_id) == str(card_id):
			sel_user = user
	logf = Log.objects.filter(card_id=card_id)

		
	dataset = {'use': sel_user, 'log': logf}
	return render(request, 'attendance/search.html', dataset)

def download_student_data(request):
    # content-type of response
    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="StudentData.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("Student Data")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # column header names
    columns = [ 'Name','Class', 'MASV', 'Phone', 'Sex', 'Email']
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    # get student data from the database
    students = Student.objects.all()
    for student in students:
        row_num += 1
        ws.write(row_num, 0, student.name, font_style)
        ws.write(row_num, 1, student.class_name, font_style)
        ws.write(row_num, 2, student.masv, font_style)
        ws.write(row_num, 3, student.phone, font_style)
        ws.write(row_num, 4, student.sex, font_style)
        ws.write(row_num, 5, student.email, font_style)
    wb.save(response)
    return response

def card_delete(request, id):
    try:
        student = get_object_or_404(Student, id=id)
        student.delete()
        return JsonResponse({'message': 'Xóa thành công!'}, status=200)
    except Student.DoesNotExist:
        return JsonResponse({'error': 'Sinh viên không tồn tại.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

import xlrd
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Log

@csrf_exempt
def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            workbook = xlrd.open_workbook(file_contents=uploaded_file.read())
            sheet = workbook.sheet_by_index(0)

            data = []
            # Đọc từng hàng từ file Excel
            for row_idx in range(1, sheet.nrows):  # Bỏ qua hàng tiêu đề
                row = sheet.row_values(row_idx)
                data.append(row)

            # Trả về dữ liệu để hiển thị trước khi lưu
            return JsonResponse({'success': True, 'data': data})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'File không hợp lệ hoặc phương thức không phải POST.'})

@csrf_exempt
def save_uploaded_data(request):
    if request.method == 'POST':
        try:
            json_data = request.body.decode('utf-8')
            data_list = json.loads(json_data)

            # Xóa toàn bộ dữ liệu cũ
            Student.objects.all().delete()
            Log.objects.all().delete()

            # Lưu dữ liệu mới từ file Excel
            for data in data_list:
                name, class_name, masv, phone, sex, email = data
                Student.objects.create(
                    name=name,
                    class_name=class_name,
                    masv=masv,
                    phone=phone,
                    sex=sex,
                    email=email
                )

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})

    return JsonResponse({'success': False, 'error_message': 'Chỉ chấp nhận yêu cầu POST.'})


def CardUidDetailApiView(request, pk):
	student = get_object_or_404(Student, card_id=pk)
	return JsonResponse({
			'id': student.id,
			'name': student.name,
			'card_id': student.card_id,
			'phone': student.phone,
			'masv': student.masv,
			'sex': student.sex,
			'email':student.email,

			
		})
        