import csv
import json
import xlwt
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser

from django.utils.encoding import smart_str
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from .models import Student, Log



from django.shortcuts import redirect
import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import xlsxwriter
import xlrd

global stat
stat = ''
# Create your views here.
global selected
selected = None


def index1(request):
    logs = Log.objects.all().order_by('date')  # Sắp xếp các đối tượng Log theo thứ tự từ mới nhất đến cũ nhất
    dataset = {'log': logs}
    return render(request, 'attendance/attendance.html', dataset)



def index(request):
    logs = Log.objects.order_by('date')  # Sắp xếp theo thời gian vào
    return render(request, 'attendance/index.html', {'logs': logs})
from django.http import JsonResponse
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def process(request):
    card = request.GET.get('card_id', None)
    users = Student.objects.filter(card_id=int(card))

    if users.exists():
        user = users.first()
        status, masv = attend(user)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'notifications',  # Tên nhóm (group) để gửi thông báo
            {
                'type': 'send_notification',  # Loại thông báo
                'message': "ghiihihih"  # Nội dung thông báo
            }
        )
        return JsonResponse({'status': status, 'maSV': masv})
    else:
        new_student = Student(card_id=card)
        new_student.save()
        return JsonResponse({'status': 'register_done', 'maSV': None})

def attend(user):
    if user.name is None:
        return 'add_infor', None
    
    logs = Log.objects.filter(card_id=user.card_id).order_by('-ida')
    
    if len(logs) == 0:
        size_Log = Log.objects.count()
        new_log, created = Log.objects.update_or_create(
            card_id=user.card_id,
            date=datetime.datetime.now().date(),
            time_in=datetime.datetime.now(),
            defaults={
                'ida': size_Log,
                'name': user.name,
                'phone': user.phone,
                'masv': user.masv,
                'time_out': None,
            }
        )
        return 'check_in', user.masv
    else:
        first_log = logs.first()
        if first_log.time_out is None:
            first_log.time_out = datetime.datetime.now()
            first_log.save()
            return 'check_out', user.masv
        else:
            size_Log = Log.objects.count()
            new_log, created = Log.objects.update_or_create(
                card_id=user.card_id,
                date=datetime.datetime.now().date(),
                time_in=datetime.datetime.now(),
                defaults={
                    'ida': size_Log,
                    'name': user.name,
                    'phone': user.phone,
                    'masv': user.masv,
                    'time_out': None,
                }
            )
            return 'check_in', user.masv


def details1(request):
    users = Student.objects.all().order_by('id')
    userset = {'users': users}
    return render(request, 'attendance/userdetails.html', userset)


def details(request):
	return render(request, 'attendance/details.html')


def manage1(request):
    users = Student.objects.all().order_by('id')
    userset = {'users': users}
    global stat
    stat = ''
    return render(request, 'attendance/allusers.html', userset)

def manage(request):
    users = Student.objects.all().order_by('id')
    context = {'users': users} 
    return render(request, 'attendance/manage.html', context)


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
    card_id = request.POST.get('card_id')
    masv = request.POST.get('masv')
    phone = request.POST.get('phone')
    email = request.POST.get('email')
    sex = request.POST.get('sex')

    
    # Tạo một đối tượng Student mới và lưu vào cơ sở dữ liệu
    new_student = Student(
        name=name,
        card_id=card_id,
        masv=masv,
        phone=phone,
        email=email,
        sex=sex
    )
    new_student.save()
    
    # Chuyển hướng người dùng đến một trang hoặc URL khác sau khi thêm thành công
    return redirect('/manage')
	
def edit(request):
  
    student = get_object_or_404(Student, card_id=request.POST.get('card_id'))

   
    student.name = request.POST.get('name')
    student.masv = request.POST.get('masv')
    student.phone = request.POST.get('phone')
    student.email = request.POST.get('email')
    student.sex = request.POST.get('sex')
    
   
    student.save()
    
   
    return redirect('/manage')

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
    columns = ['ID', 'Name', 'MASV', 'Phone', 'Sex', 'Email']
    # write column headers in sheet
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    # get student data from the database
    students = Student.objects.all()
    for student in students:
        row_num += 1
        ws.write(row_num, 0, student.card_id, font_style)
        ws.write(row_num, 1, student.name, font_style)
        ws.write(row_num, 2, student.masv, font_style)
        ws.write(row_num, 3, student.phone, font_style)
        ws.write(row_num, 4, student.sex, font_style)
        ws.write(row_num, 5, student.email, font_style)
    wb.save(response)
    return response

def delete(request,pk):
    
	Student.objects.filter(card_id=pk).delete()

	return HttpResponse('xoas ok')


def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            uploaded_file = request.FILES['file']
            workbook = xlrd.open_workbook(file_contents=uploaded_file.read())
            sheet = workbook.sheet_by_index(0)

            # Lấy dữ liệu từ sheet Excel và chuyển đổi thành danh sách các hàng
            data = []
            for row_idx in range(sheet.nrows):
                row = sheet.row_values(row_idx)
                data.append(row)

            # Trả về dữ liệu dưới dạng JSON
            return JsonResponse({'success': True, 'data': data})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Không có tệp được gửi hoặc phương thức không hợp lệ.'})




def update_student(request):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON từ request body
            json_data = request.body.decode('utf-8')
            data_list = json.loads(json_data)

            # Xóa tất cả sinh viên trong cơ sở dữ liệu
            Student.objects.all().delete()

            # Thêm lại sinh viên từ dữ liệu mới
            for data in data_list:
                card_id, name, masv, phone, sex, email = data

                Student.objects.create(
                    card_id=card_id,
                    name=name,
                    masv=masv,
                    phone=phone,
                    sex=sex,
                    email=email
                )

            return JsonResponse({'success': True})

        except json.JSONDecodeError as e:
            return JsonResponse({'success': False, 'error_message': f"Lỗi khi phân tích chuỗi JSON: {e}"})
        except Exception as e:
            return JsonResponse({'success': False, 'error_message': str(e)})
    else:
        return JsonResponse({'success': False, 'error_message': 'Endpoint chỉ chấp nhận yêu cầu POST.'})


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
        