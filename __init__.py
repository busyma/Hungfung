import os
import sqlite3
from datetime import datetime, date


from flask import Flask, render_template, url_for, flash, redirect, request
from forms import NewEmployeeForm, update_employee_info_form, RemoveEmployeeForm, UpdateEmployeeFilloutFrom ,PayrollForm, ContactForm, RemoveContactForm, Add_shift_form, get_shifts_form, GeneratePayStub
from wtforms.fields import Label 


TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')

def create_app(test_config=None):
        
        # create and configure the app
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_mapping(
                SECRET_KEY='cmpt354',
                DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
        )

        if test_config is None:
                # load the instance config, if it exists, when not testing
                app.config.from_pyfile('config.py', silent=True)
        else:
                # load the test config if passed in
                app.config.from_mapping(test_config)

        # ensure the instance folder exists
        try:
                os.makedirs(app.instance_path)
        except OSError:
                pass
        
        #Turn the results from the database into a dictionary
        def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                        d[col[0]] = row[idx]
                return d
        
        def getEmployeeID(fname,lname):
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                query = ''' SELECT EmployeeID
                                 FROM Employee
                                 WHERE Fname = ? AND Lname = ?''' 

                cur.execute(query,(fname,lname))
                employee_id = cur.fetchall()[0]['EmployeeID']
                conn.commit()
                cur.close()
                return employee_id
        

        @app.route('/')
        def index():
                return render_template('index.html')

        

#################################################################################### Employee Pages 

        @app.route('/employee', methods=['GET', 'POST'])
        def employee():
                
                return render_template('employee.html')

        @app.route('/employee/add_new_employee', methods=['GET', 'POST'])
        def add_new_employee():
                form=NewEmployeeForm()
                
                global TODAYS_DATE 
                if form.validate_on_submit():
                        
                        if(len(form.employee_middle_name.data) == 0):
                                # no middle name
                                form.employee_middle_name.data = "NULL"
                        
                        conn = sqlite3.connect("instance/flaskr.sqlite")
                        c = conn.cursor()
                        c.execute("PRAGMA foreign_keys=on")
                        #use next available ID
                        c.execute('''
                                SELECT MAX(EmployeeID)
                                FROM Employee
                                '''
                                )
                        Employee_id_dict = list(c.fetchall())
                        EMPLOYEE_ID = str(int(Employee_id_dict[0][0]) + 1)
                        print ("Max employee ID: " + EMPLOYEE_ID)
                        
                      
                        #Add the new employee into the 'Employee' table
                        query = '''insert into Employee VALUES (?, ?, ?, ?, ?, ?, ?,?)'''
                        c.execute(query, (EMPLOYEE_ID,
                                form.employee_SIN.data,
                                form.employee_date_of_birth.data,
                                TODAYS_DATE,
                                form.employee_first_name.data,
                                form.employee_middle_name.data,
                                form.employee_last_name.data,
                                form.employee_Address.data))

                        print("role = " + form.employee_role.data)
                        if (form.employee_role.data == "Office"):
                                # add to office table
                                print("OFFICE!!")
                                query = '''insert into Office VALUES (?, ?)'''
                                c.execute(query, (EMPLOYEE_ID, int(form.employee_salary.data)))
                        
                        else:
                                # add to operations table
                                print("OPERATIONS!!")
                                query = 'insert into Operations VALUES (?, ?)'
                                c.execute(query, (EMPLOYEE_ID, float(form.employee_salary.data)))


                        # format phone number to: (xxx) xxx-xxxx
                        tmp = form.employee_phone.data
                        first = tmp[0:3]
                        second = tmp[3:6]
                        third = tmp[6:10]
                        format_number = "(" + first + ") " + second + "-" + third
                        

                        # Add their Phone Number
                        query = 'insert into Phone values (?,?)'
                        c.execute(query, (format_number, EMPLOYEE_ID) )

                
                        conn.commit()
                        c.close()

                        flash(f'{form.employee_first_name.data} {form.employee_last_name.data}: added to database', 'success')
                        return redirect(url_for('add_new_employee'))
                        

                return render_template('add_new_employee.html',form=form)

        @app.route('/employee/update_employee_info', methods=['GET', 'POST'])
        def update_employee_info():
                drop_down_form = update_employee_info_form()

                # open database connection
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # Populate drop down dynamically
                cur.execute(''' SELECT EmployeeID, Fname, Lname FROM Employee''')
                employees = cur.fetchall()
                employees_list=[(employee['Fname'] + " " + employee['Lname']) for employee in employees]
                employees_list.insert(0,"")
                drop_down_form.employee_update.choices = employees_list

                if drop_down_form.validate_on_submit():

        
                        fname = drop_down_form.employee_update.data.split(" ")[0]
                        lname = drop_down_form.employee_update.data.split(" ")[1]

                        conn.commit()
                        cur.close()

                        return redirect(url_for('update_fill_out', fname = fname , lname = lname))
                        
                
                conn.commit()
                cur.close()
                
                return render_template('update_employee_info.html',form=drop_down_form)

        
        @app.route('/update_fill_out/<fname>/<lname>', methods=['GET', 'POST'])
        def update_fill_out(fname , lname):
                update_form = UpdateEmployeeFilloutFrom()

                # open database connection
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")

                # get the ID for the selected employee
                query = '''
                        SELECT E.EmployeeID
                        FROM Employee E
                        WHERE Fname = ? AND Lname = ? 
                        '''
                cur.execute(query,(fname,lname))
                tmp = cur.fetchall()
                ID = tmp [0]['EmployeeID']
                print (tmp)
                print ("size of tmp: "+ str(len(tmp)))
                # get the employee's info 
                query = '''SELECT *, PhoneNumber FROM Employee, Phone 
                           WHERE EmployeeID = ? AND Phone.ID = Employee.EmployeeID'''
                cur.execute(query , (ID))
                current_vals = cur.fetchall()

                # display current values 
                update_form.employee_Address.label.text = str(current_vals[0]['Address'])
                update_form.employee_first_name.label.text = fname
                update_form.employee_middle_name.label.text = str(current_vals[0]['Mname'])
                update_form.employee_last_name.label.text = lname
                update_form.employee_SIN.label.text = str(current_vals[0]['SIN'])
                update_form.employee_phone.label.text = str(current_vals[0]['PhoneNumber'])
                update_form.employee_date_of_birth.label.text = str(current_vals[0]['DateofBirth'])
                update_form.employee_first_name.label.text = fname
              

                # query the Office table to see what department the employee is in
                query = "SELECT * FROM Office WHERE ID = ?"
                cur.execute(query,(ID))
                Department = cur.fetchall()

                # query is empty, employee is in operations
                if(len(Department) == 0):
                        d_name = 'Operations'
                        update_form.employee_role.label.text = 'Operations'
                        update_form.employee_role.choices = ['Operations', 'Office']
                        cur.execute("SELECT WagePerHour From Operations Where ID = ?", (ID))
                        wage = cur.fetchall()[0]['WagePerHour']
                        update_form.employee_salary.label.text = wage
                else:
                        d_name = 'Office'
                        update_form.employee_role.label.text= 'Office'
                        update_form.employee_role.choices = ['Office', 'Operations']
                        update_form.employee_salary.label.text = Department[0]['Salary']

                full_name = fname + " " + lname 

                if update_form.validate_on_submit():
                        # check which fields have changed and update them
                        
                        if (len(update_form.employee_SIN.data) != 0):
                                cur.execute("Update Employee SET SIN = ? WHERE EmployeeID = ?" ,( update_form.employee_SIN.data, ID))
                        if (len(update_form.employee_date_of_birth.data) != 0):
                                cur.execute("Update Employee SET DateofBirth = ? WHERE EmployeeID = ?" , (update_form.employee_date_of_birth.data , ID))
                        if (len(update_form.employee_first_name.data) != 0):
                                cur.execute("Update Employee SET Fname = ? WHERE EmployeeID = ?" , (update_form.employee_first_name.data, ID))
                        if (len(update_form.employee_last_name.data) != 0):
                                cur.execute("Update Employee SET Lname = ? WHERE EmployeeID = ?" ,( update_form.employee_last_name.data, ID))
                        if (len(update_form.employee_middle_name.data) != 0):
                                cur.execute("Update Employee SET Mname = ? WHERE EmployeeID = ?" , (update_form.employee_middle_name.data, ID))
                        if (len(update_form.employee_Address.data) != 0):
                                cur.execute("Update Employee SET Address = ? WHERE EmployeeID = ?" , (update_form.employee_Address.data, ID))
                        if (len(update_form.employee_phone.data) != 0):
                                # format phone number before adding to DB
                                tmp = update_form.employee_phone.data
                                first = tmp[0:3]
                                second = tmp[3:6]
                                third = tmp[6:10]
                                format_number = "(" + first + ") " + second + "-" + third
                                cur.execute("UPDATE Phone SET PhoneNumber = ? WHERE ID = ?", (format_number, ID) )

                        
                
                        
                        

                        # reflect changes in Operations and Office tables 
                        # if statemeants are used because SQL Tables can not be variables
                        print ("Name: " + fname + " Selected Role:" + str(update_form.employee_role.data))
                        if( len(update_form.employee_salary.data) != 0 ):
                                if (d_name == "Operations"):
                                        query = "DELETE FROM Operations WHERE ID = ?"
                                        cur.execute(query, (ID))
                                        

                                        if (update_form.employee_role.data == 'Office'):
                                                query = "INSERT INTO Office VALUES(?, ?)"
                                                cur.execute(query, (ID ,update_form.employee_salary.data))
                                        else:
                                                query = "INSERT INTO Operations VALUES(?, ?)"
                                                cur.execute(query, (ID ,update_form.employee_salary.data))
                                                
                                else:
                                        query = "DELETE FROM Office WHERE ID = ?"
                                        cur.execute(query, (ID))
                                        

                                        if (update_form.employee_role.data == 'Office'):
                                                query = "INSERT INTO Office VALUES(?, ?)"
                                                cur.execute(query, (ID ,update_form.employee_salary.data))
                                        else:
                                                query = "INSERT INTO Operations VALUES(?, ?)"
                                                cur.execute(query, (ID ,update_form.employee_salary.data))

                
                        conn.commit()
                        cur.close()
                        return(redirect(url_for('update_employee_info')))


                conn.commit()
                cur.close()

                return render_template('update_fill_out.html', form = update_form, name = full_name)#, form = form, name = name)

        
        @app.route('/employee/ex_employee_info', methods=['GET', 'POST'])
        def ex_employee_info():
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                cur.execute("SELECT * FROM exEmployees")
                exEmployees = cur.fetchall()
                conn.commit()
                
                return render_template('exEmployeesInfo.html',exEmployees=exEmployees)

        @app.route('/report')
        def report():
                return render_template('report.html')
        

        @app.route('/employee/remove_employee', methods=['GET', 'POST'])
        def removeEmployee():
                form = RemoveEmployeeForm()
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # list all employees
                cur.execute('''
                                SELECT E1.*
                                FROM Operations O, Employee E1
                                WHERE O.ID = E1.EmployeeID
                                UNION
                                SELECT E2.*
                                FROM Office Of, Employee E2
                                WHERE Of.ID = E2.EmployeeID
                                ORDER BY E2.Lname ASC

                        ''')
                employees = cur.fetchall()

                if form.validate_on_submit():
                        selected_employees = request.form.getlist('chkb')
                        for e in selected_employees:
                                #remove selected employees 
                                query = "DELETE FROM Employee WHERE EmployeeID = ?"
                                print("remove ID: " +str(e) +" from Employee")
                                cur.execute(query,(e))

                        cur.execute("SELECT * FROM exEmployees")
                        exEmployees = cur.fetchall()
                        conn.commit()
                        cur.close()
                        return redirect(url_for('removeEmployee'))
                
                return render_template('removeEmployee.html', form=form, employees = employees)


#################################################################################### Report Pages 
        @app.route('/report/employeeinfo', methods=['GET', 'POST'])
        def employeeinfo():
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # display operations employees
                cur.execute('''
                        SELECT E.*, P.PhoneNumber, O.WagePerHour
                        FROM Operations O, Employee E, Phone P
                        WHERE O.ID = E.EmployeeID AND P.ID = E.EmployeeID AND O.ID = P.ID
                        ORDER BY UPPER(E.Lname) ASC
                               ''')
                operations = cur.fetchall()

                #display office employees
                cur.execute('''
                        SELECT E.*, P.PhoneNumber, O.Salary  
                        FROM Office O, Employee E, Phone P
                        WHERE O.ID = E.EmployeeID AND P.ID = E.EmployeeID AND O.ID = P.ID
                        ORDER BY UPPER(E.Lname) ASC
                               ''')
                offices = cur.fetchall()
                
                conn.commit()
                cur.close()

                return render_template('employeeinfo.html', operations=operations, offices=offices,
                                        office_len=len(offices), operations_len=len(operations))

        def get_department_and_pay_from_employee_id(employee_id):
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                query = ''' SELECT *
                            FROM Employee E, Office Of
                            WHERE E.EmployeeID = ? and E.EmployeeID = Of.ID ''' 

                cur.execute(query,(employee_id))
                records = cur.fetchall()

                if len(records) == 0:
                        query = ''' SELECT *
                                FROM Employee E, Operations Op
                                WHERE E.EmployeeID = ? and E.EmployeeID = Op.ID ''' 

                        cur.execute(query,(employee_id))
                        records = cur.fetchall()
                        department_and_pay = ('operations', records[0]['WagePerHour'])
                else:
                        department_and_pay = ('office', records[0]['Salary'])

                return department_and_pay

        def get_total_hours_from_shifts(employee_id, start, end):
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                query = ''' SELECT *
                            FROM Employee E, Shift S
                            WHERE E.EmployeeID = ? and E.EmployeeID = S.ID and S.DateofShift BETWEEN ? and ? ''' 

                cur.execute(query,(employee_id, start, end))
                records = cur.fetchall()

                total_hours = 0
                
                for r in records:
                        total_hours += abs(r['EndTime'] - r['StartTime'])

                return total_hours


        @app.route('/report/payroll', methods=['GET', 'POST'])
        def payroll():
                global TODAYS_DATE
                form = PayrollForm()
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # Populate drop down dynamically
                cur.execute(''' SELECT EmployeeID, Fname, Lname FROM Employee''')
                employees = cur.fetchall()
                employees_list=[(employee['Fname'] + " " + employee['Lname']) for employee in employees]
                employees_list.insert(0,"")
                form.employee_filter.choices = employees_list
                
                generate_pay_stub_form = GeneratePayStub()
                generate_pay_stub_form.employee_filter_pay_stub.choices = employees_list
                if generate_pay_stub_form.validate_on_submit():
                        fname = generate_pay_stub_form.employee_filter_pay_stub.data.split(" ")[0]
                        lname = generate_pay_stub_form.employee_filter_pay_stub.data.split(" ")[1]
                        employee_id = getEmployeeID(fname,lname)

                        department, pay = get_department_and_pay_from_employee_id(employee_id)          # pay can be salary or wage
                        start = generate_pay_stub_form.start_date.data
                        end = generate_pay_stub_form.end_date.data
                        num_days = abs((end - start).days)

                        full_name = fname+' '+lname

                        if department == 'office':
                                total_pay = ((pay/12)/30)*num_days                                
                        elif department == 'operations':
                                total_hours_worked = get_total_hours_from_shifts(employee_id, start, end)
                                total_pay = total_hours_worked*pay
                        
                        new_cheque_number_query = '''Select MAX(ChequeNumber) From Payroll'''
                        cur.execute(new_cheque_number_query)
                        new_cheque_number = cur.fetchall()
                        

                        if (new_cheque_number[0]['MAX(ChequeNumber)'] is None):
                                new_cheque_number = 10000
                        else:
                                new_cheque_number = int(new_cheque_number[0]['MAX(ChequeNumber)'])+1

                        insert_query = '''INSERT INTO Payroll VALUES (?,?,?,?,?,?,?,?)'''

                        data_row = (new_cheque_number, TODAYS_DATE, total_pay, total_pay*0.02, total_pay*0.02, total_pay*0.12, total_pay*0.12, employee_id)
                        cur.execute(insert_query, data_row)

                        conn.commit()
                        cur.close()
                        flash('New Pay Stub Generated', 'success')

                elif form.validate_on_submit():
                        fname = form.employee_filter.data.split(" ")[0]
                        lname = form.employee_filter.data.split(" ")[1]
                        ID = getEmployeeID(fname, lname)

                        # get pay stubs
                        query = '''SELECT E.Fname, E.Lname, P.ChequeNumber, P.PayrollDate, P.GrossPay
                                FROM Employee E, Payroll P
                                WHERE P.ID = ? AND E.EmployeeID = P.ID AND P.PayrollDate between ? and ? 
                                Order by P.PayrollDate desc
                                LIMIT ?'''
                        
                        # check which filter is selected
                        if (form.payroll_date_range.data == "YTD"):
                                #Show pay stubs from start of year
                                start = TODAYS_DATE[0:4] + "-01-01"
                                end = TODAYS_DATE
                                limit = 100
                        else:
                                #Show up to the last 25 stubs
                                start = "2000-01-01"
                                end = TODAYS_DATE
                                limit = 25
                        cur.execute(query, (ID, start ,end ,limit))
                        stubs = cur.fetchall()

                        # get the gross pay
                        query = '''SELECT SUM(P.GrossPay) as grossPay
                                FROM Payroll P
                                WHERE P.ID = ? AND P.PayrollDate between ? and ? LIMIT ?'''
                        cur.execute(query, (ID, start ,end ,limit))
                        gross_pay = cur.fetchall()

                        print (gross_pay)
                        conn.commit()
                        cur.close()

                        return render_template('payroll_data.html', stubs = stubs, gross_pay = gross_pay[0]['grossPay']) 
                return render_template('payroll.html', form = form, generate_pay_stub_form = generate_pay_stub_form)


        @app.route('/report/tax', methods=['GET', 'POST'])
        def tax():
                #form=NewEmployeeForm()
                return render_template('tax.html')
# ################################## shift pages #####################################################



        @app.route('/shift', methods=['GET', 'POST'])
        def shift():
                
                return render_template('shift.html')

        @app.route('/shift/timecard', methods=['GET', 'POST'])
        def timecard():
                form = get_shifts_form()
                # Populate drop down dynamically
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                cur.execute(''' SELECT EmployeeID, Fname, Lname FROM Employee''')
                employees = cur.fetchall()
                employees_list=[(employee['Fname'] + " " + employee['Lname']) for employee in employees]
                employees_list.insert(0,"")
                form.employee_filter.choices = employees_list
                if form.validate_on_submit():
                        employee_full_name = form.employee_filter.data
                        fname = form.employee_filter.data.split(" ")[0]
                        lname = form.employee_filter.data.split(" ")[1]
                        emloyee_id=getEmployeeID(fname,lname)

                        query ='SELECT * FROM Shift WHERE ID = ?'
                        cur.execute(query, (emloyee_id,))
                        shifts=cur.fetchall()
                        conn.commit()
                        cur.close()
                        return render_template('timecard_data.html',shifts=shifts, employee_full_name=employee_full_name)
                        
                        
                return render_template('timecard.html', form=form)


        @app.route('/shift/add_shit', methods=['GET', 'POST'])
        def add_shift():
                form = Add_shift_form()
                 # Populate drop down dynamically
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                cur.execute(''' SELECT EmployeeID, Fname, Lname FROM Employee''')
                employees = cur.fetchall()
                employees_list=[(employee['Fname'] + " " + employee['Lname']) for employee in employees]
                employees_list.insert(0,"")
                form.employee_filter.choices = employees_list
                if form.validate_on_submit():
                        # calculating the next shift id to be added
                        cur.execute('''
                                SELECT MAX(ShiftID)
                                FROM Shift
                                '''
                                )
                        Shift_ID_dictionary = cur.fetchall()
                        max_shift_id = Shift_ID_dictionary[0]['MAX(ShiftID)']
                        next_shift_id_to_be_added = str(int(max_shift_id)+1)
                        # calculating employee id from fname and lastname
                        fname = form.employee_filter.data.split(" ")[0]
                        lname = form.employee_filter.data.split(" ")[1]
                        emloyee_id=getEmployeeID(fname,lname)
                        # Now that we have shiftID and employeeID we can generate the new shift
                        query = 'insert into Shift VALUES (?, ?, ?, ?, ?)'
                        cur.execute(query, (emloyee_id,next_shift_id_to_be_added,form.shift_start_time.data,form.sift_end_time.data,form.date_of_shift.data))
                        conn.commit()
                        cur.close()

                        flash(f'Shift {next_shift_id_to_be_added} was added for {fname} {lname}', 'success')
                        return redirect(url_for('add_shift'))
                return render_template('add_shift.html', form=form)

        
#################################################################################### Emergency Contact Pages 
        @app.route('/emergency', methods=['GET', 'POST'])
        def emergency():
                connection = sqlite3.connect("instance/flaskr.sqlite")
                connection.row_factory = dict_factory
                cur = connection.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # get emergency contact info
                cur.execute('''
                                SELECT EC.ContactName, EC.PhoneNumber, 
                                EC.Relation, E.Fname, E.Lname
                                FROM EmergencyContact EC, Employee E 
                                WHERE EC.ID = E.EmployeeID 
                                ORDER BY E.Lname, E.Fname ASC
                         ''')
                emergency_contacts = cur.fetchall()

                connection.commit()
                cur.close()
                return render_template('emergency.html',  emergency_contacts = emergency_contacts)
        
        @app.route('/add_emergency_contact', methods=['GET', 'POST'])
        def add_emergency_contact():
                form =  ContactForm()

                # open database connection
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")
                # Populate drop down dynamically
                cur.execute(''' SELECT EmployeeID, Fname, Lname FROM Employee''')
                employees = cur.fetchall()
                employees_list=[(employee['Fname'] + " " + employee['Lname']) for employee in employees]
                employees_list.insert(0,"")
                form.emergency_contact_employee.choices = employees_list

                if form.validate_on_submit():
                        fname = form.emergency_contact_employee.data.split(" ")[0]
                        lname = form.emergency_contact_employee.data.split(" ")[1]
                        query = '''
                                SELECT E.EmployeeID
                                FROM Employee E
                                WHERE Fname = ? AND Lname = ? 
                                '''
                        cur.execute(query,(fname,lname))
                        ID = cur.fetchall()[0]['EmployeeID']
                        
                        # format phone number to: (xxx) xxx-xxxx
                        tmp = form.emergency_contact_phone.data
                        first = tmp[0:3]
                        second = tmp[3:6]
                        third = tmp[6:10]
                        format_number = "(" + first + ") " + second + "-" + third

                        query = '''
                                INSERT INTO EmergencyContact VALUES(?,?,?,?) 
                                '''
                        cur.execute(query, (form.emergency_contact_name.data, format_number , 
                                             form.emergency_contact_relation.data, ID))
                        
                        conn.commit()
                        cur.close()

                        flash(f'{form.emergency_contact_name.data}: added as Emergency Contact for {form.emergency_contact_employee.data}', 'success')
                        return redirect(url_for('add_emergency_contact'))


                return(render_template('add_emergency_contact.html', form = form))

        
        @app.route('/delete_emergency_contact', methods=['GET', 'POST'])
        def delete_emergency_contact():
                form = RemoveContactForm()
                connection = sqlite3.connect("instance/flaskr.sqlite")
                connection.row_factory = dict_factory
                cur = connection.cursor()
                cur.execute("PRAGMA foreign_keys=on")

                # get emergency contact info
                cur.execute('''
                                SELECT EC.ContactName, EC.PhoneNumber, 
                                EC.Relation, E.Fname, E.Lname
                                FROM EmergencyContact EC, Employee E 
                                WHERE EC.ID = E.EmployeeID 
                                ORDER BY E.Lname, E.Fname ASC
                        ''')
                emergency_contacts = cur.fetchall()

                if form.validate_on_submit():
                        selected_contacts = request.form.getlist('chk')

                        #loop over selected employees removing each one
                        for c in selected_contacts:
                                contact_name = c.split("+")[0]
                                employee_Fname = c.split("+")[1]
                                employee_Lname = c.split("+")[2]

                                # find the ID to remove
                                query = "SELECT E.EmployeeID FROM Employee E WHERE E.Fname = ? AND E.Lname =?"
                                cur.execute(query,(employee_Fname, employee_Lname))
                                ID = cur.fetchall()[0]['EmployeeID']
                                print(ID)
                                # delete contact
                                query = '''DELETE FROM EmergencyContact 
                                        WHERE ContactName = ? AND ID = ?  '''
                                cur.execute(query,(contact_name, ID))


                        connection.commit()
                        cur.close()
                        
                        return(redirect(url_for('emergency')))

                return(render_template('delete_emergency_contact.html', form = form, emergency_contacts = emergency_contacts))



        
        @app.route('/holiday', methods=['GET', 'POST'])
        def holiday():
                conn = sqlite3.connect("instance/flaskr.sqlite")
                conn.row_factory = dict_factory
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys=on")

                query = '''

                        SELECT E.EmployeeID, E.Fname, E.Mname, E.Lname
                        FROM Employee E
                        WHERE NOT EXISTS (
                                SELECT H.DateofHoliday
                                FROM Holiday H
                                WHERE H.DateofHoliday NOT IN (
                                        SELECT DISTINCT S.DateofShift
                                        FROM Shift S
                                        WHERE S.ID = E.EmployeeID
                                )

                        )

                        '''
                cur.execute(query)
                employees = cur.fetchall()
                conn.commit()
                cur.close()
                return(render_template('holiday.html', employees = employees))


        from . import db
        db.init_app(app)

        return(app)