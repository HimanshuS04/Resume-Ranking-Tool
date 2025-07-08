from numpy import add
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extras import DictCursor
import os
import bcrypt

def connect():
  conn = psycopg2.connect(os.getenv('AZURE_POSTGRESQL_CONNECTIONSTRING'))
  return conn

def hash_password(password):
  # Generate a salt and hash the password
  salt = bcrypt.gensalt()
  hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
  return hashed_password.decode('utf-8')  # Store the hashed password as a string

def sign_up(name, email, plain_password, user_type, company_name=None):
  # Hash the password securely
  password_hash = hash_password(plain_password)

  conn = None
  try:
      conn = connect()

      cur = conn.cursor(cursor_factory=RealDictCursor)

      # Check if the email already exists
      check_query = "SELECT UserID FROM Users WHERE Email = %s"
      cur.execute(check_query, (email,))
      user_exists = cur.fetchone()

      if user_exists:
          print("Error: User with this email already exists.")
          return 1

      # Insert new user into the Users table
      insert_query = """
      INSERT INTO Users (Name, Email, PasswordHash, UserType, CompanyName)
      VALUES (%s, %s, %s, %s, %s)
      RETURNING UserID;
      """
      cur.execute(insert_query, (name, email, password_hash, user_type, company_name))

      # Commit the transaction
      conn.commit()

      # Fetch the new user ID
      new_user_id = cur.fetchone()["UserID"]
      print(f"User signed up successfully with UserID: {new_user_id}")
      return new_user_id

  except (Exception, psycopg2.DatabaseError) as error:
      print(f"Error: {error}")
      return False

  finally:
      if conn is not None:
          conn.close()







def verify_password(plain_password, hashed_password):
  # Convert hashed_password to bytes if it is a string
  if isinstance(hashed_password, str):
      hashed_password = hashed_password.encode('utf-8')

  # Check that the provided password matches the hashed password
  return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def sign_in(email, plain_password):
  conn = None
  try:
      conn = connect()

      cur = conn.cursor(cursor_factory=RealDictCursor)

      select_query = "SELECT UserID, PasswordHash, usertype FROM Users WHERE Email = %s"
      cur.execute(select_query, (email,))
      user_record = cur.fetchone()

      if not user_record:
          print("Error: No user found with this email.")
          return False

      user_id = user_record["userid"]
      stored_hashed_password = user_record["passwordhash"]

      if verify_password(plain_password, stored_hashed_password):
          print(f"User signed in successfully with UserID: {user_id}")
          print([user_id, user_record["usertype"]])
          return [user_id, user_record["usertype"]]
      else:
          print("Error: Incorrect password.")
          return False

  except (Exception, psycopg2.DatabaseError) as error:
      print(f"Error: {error}")
      return False

  finally:
      if conn is not None:
          conn.close()




def add_job(employer_id, title, description, location, salary, date_closing, status='Open'):
  # Database connection parameters - update these with your actual database details
  conn = None
  try:
      conn = connect()

      # Create a cursor object to interact with the database
      cur = conn.cursor(cursor_factory=RealDictCursor)

      # Insert the job details into the Jobs table
      insert_query = """
      INSERT INTO Jobs (EmployerID, Title, Description, Location, Salary, DatePosted, DateClosing, Status)
      VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, %s, %s)
      RETURNING JobID;
      """
      cur.execute(insert_query, (employer_id, title, description, location, salary, date_closing, status))

      # Commit the transaction
      conn.commit()

      # Fetch the new JobID
      new_job_id = cur.fetchone()["JobID"]
      print(f"Job added successfully with JobID: {new_job_id}")
      return new_job_id

  except (Exception, psycopg2.DatabaseError) as error:
      print(f"Error: {error}")
      return False

  finally:
      # Close the database connection
      if conn is not None:
          conn.close()





def jobs():
    conn = connect()
    cur = conn.cursor(cursor_factory=DictCursor)

    # Updated SQL query to join Jobs and Employers to get the company name
    cur.execute('''
        SELECT 
            jobs.jobid, 
            jobs.title, 
            jobs.description, 
            jobs.location, 
            jobs.salary, 
            jobs.dateposted, 
            jobs.dateclosing, 
            jobs.status,
            users.companyname,
            users.name
        FROM jobs
        JOIN users ON jobs.employerid = users.userid
        ORDER BY jobs.dateposted DESC;
    ''')

    jobs = cur.fetchall()
    cur.close()
    conn.close()
    return jobs


def apply(job_id, employee_id, score):
    conn=connect();
    cur=conn.cursor(cursor_factory=DictCursor)
    cur.execute('''
        INSERT INTO applications (jobid, employeeid, score ) VALUES (%s, %s, %s)
        ''',(job_id, employee_id, score,))
    conn.commit()
    cur.close()
    conn.close()

def get_application_status(employee_id):
    """
    Function to get the status of applications submitted by a specific employee, including job title and company name.

    :param employee_id: The ID of the employee whose application statuses are to be fetched.
    :return: A list of dictionaries containing application details, or an empty list if no applications are found.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor(cursor_factory=DictCursor)

        # SQL query to get the status of all applications submitted by the employee
        select_query = """
        SELECT 
            a.ApplicationID, 
            a.JobID, 
            a.ApplicationDate, 
            a.Status, 
            a.Score,
            j.Title ,
            e.CompanyName
        FROM Applications a
        JOIN Jobs j ON a.JobID = j.JobID
        JOIN users e ON j.EmployerID = e.userID
        WHERE a.EmployeeID = %s
        ORDER BY a.ApplicationDate DESC;
        """

        # Execute the query
        cur.execute(select_query, (employee_id,))

        # Fetch all results
        applications = cur.fetchall()

        # Close the cursor
        cur.close()

        # Return the list of application statuses
        return applications

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return []

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()




def get_job_results(job_id):
    """
    Function to get the results of a specific job, returning the usernames, emails, and scores of applicants.

    :param job_id: The ID of the job for which the results are to be fetched.
    :return: A list of dictionaries containing applicant details (username, email, score), or an empty list if no applications are found.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor(cursor_factory=DictCursor)

        # SQL query to get the usernames, emails, and scores of all applicants for the job
        select_query = """
        SELECT 
            u.userid,
            u.name,
            u.Email,
            a.applicationid,
            a.Score,
            a.jobid
        FROM Applications a
        JOIN Users u ON a.EmployeeID = u.UserID
        WHERE a.JobID = %s
        ORDER BY a.Score DESC;
        """

        # Execute the query
        cur.execute(select_query, (job_id,))

        # Fetch all results
        applicants = cur.fetchall()

        # Close the cursor
        cur.close()

        # Return the list of applicant details
        return applicants

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return []

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()






def get_jobs_by_employer(employer_id):
    """
    Function to get all jobs posted by a specific employer, returning the JobID and JobTitle.

    :param employer_id: The ID of the employer whose jobs are to be fetched.
    :return: A list of dictionaries containing job details (JobID and JobTitle), or an empty list if no jobs are found.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor(cursor_factory=DictCursor)

        # SQL query to get all jobs posted by the employer
        select_query = """
        SELECT 
            JobID, 
            Title 
        FROM Jobs
        WHERE EmployerID = %s
        ORDER BY JobID DESC;
        """

        # Execute the query
        cur.execute(select_query, (employer_id,))

        # Fetch all results
        jobs = cur.fetchall()

        # Close the cursor
        cur.close()

        # Return the list of jobs
        return jobs

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return []

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()






def get_job_description(job_id):
    """
    Function to get the job description of a specific job by JobID.

    :param job_id: The ID of the job for which to fetch the description.
    :return: The job description if found, or None if not found.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor(cursor_factory=DictCursor)

        # SQL query to get the job description
        select_query = """
        SELECT Description
        FROM Jobs
        WHERE JobID = %s;
        """

        # Execute the query
        cur.execute(select_query, (job_id,))

        # Fetch the result
        result = cur.fetchone()

        # Close the cursor
        cur.close()

        # Return the job description if found
        if result:
            return result['description']
        else:
            print(f"No job found with JobID: {job_id}")
            return None

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return None

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()

















def accepted(application_id):
    """
    Function to update the status of a specific application to 'Accepted'.

    :param application_id: The ID of the application to update.
    :return: True if the update was successful, False otherwise.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor()

        # SQL query to update the status of the application to 'Accepted'
        update_query = """
        UPDATE Applications
        SET Status = 'Accepted'
        WHERE ApplicationID = %s;
        """

        # Execute the query
        cur.execute(update_query, (application_id,))

        # Commit the changes to the database
        conn.commit()

        

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return False

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()



def rejected(application_id):
    """
    Function to update the status of a specific application to 'Rejected'.

    :param application_id: The ID of the application to update.
    :return: True if the update was successful, False otherwise.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor()

        # SQL query to update the status of the application to 'Accepted'
        update_query = """
        UPDATE Applications
        SET Status = 'Rejected'
        WHERE ApplicationID = %s;
        """

        # Execute the query
        cur.execute(update_query, (application_id,))

        # Commit the changes to the database
        conn.commit()



    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return False

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()
  







def delete_job(job_id):
    """
    Function to delete a specific job from the database.

    :param job_id: The ID of the job to delete.
    :return: True if the deletion was successful, False otherwise.
    """
    conn = None
    try:
        # Database connection parameters - replace with your actual database details
        conn = connect()

        # Create a cursor to execute SQL commands
        cur = conn.cursor()

        # SQL query to delete the job
        delete_query = """
        DELETE FROM Jobs
        WHERE JobID = %s;
        """

        # Execute the query
        cur.execute(delete_query, (job_id,))

        # Commit the changes to the database
        conn.commit()

        # Check if any row was affected
        if cur.rowcount > 0:
            print(f"Job with ID {job_id} has been deleted.")
            return True
        else:
            print(f"No job found with ID {job_id}.")
            return False

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        return False

    finally:
        # Close the database connection
        if conn is not None:
            conn.close()



