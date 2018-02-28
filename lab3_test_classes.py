"""lab3_test_classes.py

Champlain College CSI-235, Spring 2018
The following code was adapted by Joshua Auerbach (jauerbach@champlain.edu)
from the UC Berkeley Pacman Projects (see license and attribution below).

----------------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

import test_classes
import socket
import os
from struct import Struct

HOST = "csi235.site"
UPLOAD_PORT = 8900
FIXED_LENGTH_TEST_PORT = 8901
DELIMITER_TEST_PORT = 8902

BAD_PORT = 9000

class EvalTest(test_classes.TestCase):
    """Simple test case which evals an arbitrary piece of python code.
    
    The test is correct if the output of the code given the student's
    solution matches that of the instructor's.
    """

    def __init__(self, question, test_dict):
        super().__init__(question, test_dict)
        self.preamble = compile(test_dict.get('preamble', ""),
                                "%s.preamble" % self.get_path(), 'exec')
        self.test = compile(test_dict['test'], "%s.test" % self.get_path(),
                            'eval')
        self.success = test_dict['success']
        self.failure = test_dict['failure']

    def eval_code(self, module_dict):
        bindings = dict(module_dict)
        exec(self.preamble, bindings)
        return str(eval(self.test, bindings))

    def execute(self, grades, module_dict, solution_dict):
        result = self.eval_code(module_dict)
        if result == solution_dict['result']:
            grades.add_message('PASS: %s' % self.path)
            grades.add_message('\t%s' % self.success)
            return True
        else:
            grades.add_message('FAIL: %s' % self.path)
            grades.add_message('\t%s' % self.failure)
            grades.add_message('\tstudent result: "%s"' % result)
            grades.add_message('\tcorrect result: "%s"' %
                               solution_dict['result'])

        return False

    def write_solution(self, module_dict, file_path):
        handle = open(file_path, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# The result of evaluating the test must equal ')
        handle.write('the below when cast to a string.\n')

        handle.write('result: "%s"\n' % self.eval_code(module_dict))
        handle.close()
        return True


class Lab3Test(test_classes.TestCase):

    def __init__(self, question, test_dict):
        super().__init__(question, test_dict)
        self.good_files = ["test_files/good_file1.dat", 
                           "test_files/good_file2.dat", "upload_client.py"]
        self.bad_files = ["test_files/bad_file.dat"]
        

    def write_solution(self, module_dict, file_path):
        handle = open(file_path, 'w')
        handle.write('# This is the solution file for %s.\n' % self.path)
        handle.write('# This file is left blank intentionally.\n')
        handle.close()
        return True

        
    def add_pass_message(self, grades):
        grades.add_message('PASS: {}'.format(self.path))   
        
    def add_fail_messages(self, grades, messages):
        grades.add_message('FAIL: {}'.format(self.path))    
        for message in messages:
            grades.add_message('\t' + message)

    def get_socket(self, client, include_key=False):
        for key, value in client.__dict__.items():
            if(isinstance(value, socket.socket)): 
                if include_key:       
                    return key, value
                return value

    
class BasicUploadClientTest(Lab3Test):

    def execute(self, grades, module_dict, solution_dict):
        upload_client = module_dict["upload_client"]        
        passing_all = True
        
        # test timeout
        #grades.add_message("Testing timeout...")        
        #try:
        #    client = upload_client.UploadClient(HOST, BAD_PORT)        
        #except socket.timeout:
        #    self.add_pass_message(grades)
        #else:
        #    self.add_fail_messages(grades, ["Did not timeout on initialization"
        #                                    " when connecting to invalid port"])
        #    passing_all = False
            

        # test connecting to upload server
        sock = None
        grades.add_message("Testing initialization...")        
        try:
            client = upload_client.UploadClient(HOST, UPLOAD_PORT)        
        except TimeoutError:
            self.add_fail_messages(grades, ["Timed out when connecting to "
                                            "valid port, check internet "
                                            "connection"])
            passing_all = False
        else:
            key, sock = self.get_socket(client, True)
            if sock:
                grades.add_message("Found socket member variable {}.".format(key)) 
                if sock.type != socket.SOCK_STREAM:
                    self.add_fail_messages(grades, 
                        ["Socket is of wrong type"])
                    passing_all = False
                        
                elif sock.family != socket.AF_INET:
                    self.add_fail_messages(grades, 
                        ["Socket is of wrong family"])
                    passing_all = False
                    
                else:
                    try:
                        sock.getpeername()
                        self.add_pass_message(grades)
                    except OSError:
                        self.add_fail_messages(grades, 
                            ["Socket is not connected"])
                        passing_all = False
                    
        if not sock:        
            self.add_fail_messages(grades, 
                ["No socket member variable found."])
            passing_all = False                

        else:
            grades.add_message("Testing closing...")             
            client.close()
            try:
                sock.getpeername()
            except OSError:
                self.add_pass_message(grades)            
            else:
                self.add_fail_messages(grades, 
                    ["Socket did not close properly"])
                passing_all = False

        
        return passing_all
        

class RecvAllTest(Lab3Test):

    def execute(self, grades, module_dict, solution_dict):
        upload_client = module_dict["upload_client"]        
        passing_all = True
        
        client = upload_client.UploadClient(HOST, FIXED_LENGTH_TEST_PORT)
        sock = self.get_socket(client)
        
        size_struct = Struct("!I")
        
        for size in [1, 1024, 4096]:
            expected_result = b"FIXED_LENGTH" * size
        
            grades.add_message("Testing recv_all " + str(len(expected_result)) + "...")
            sock.sendall(size_struct.pack(size))
                    
            result = client.recv_all(len(expected_result))
            if expected_result == result:
                self.add_pass_message(grades)    
            else:
                self.add_fail_messages(grades, 
                    ["Did not receive expected response from recv_all"])
                passing_all = False                    
        
        client.close()
        return passing_all
        
class RecvUntilDelimiterTest(Lab3Test):

    def execute(self, grades, module_dict, solution_dict):
        upload_client = module_dict["upload_client"]        
        passing_all = True
        
        client = upload_client.UploadClient(HOST, DELIMITER_TEST_PORT)
        sock = self.get_socket(client)
        
        grades.add_message("Testing recv_until_delimiter (single)...")
        sock.sendall(b"%")
        result = client.recv_until_delimiter(b"%")
        expected_result = b"DELIMITER" * 4096
        
        if result == expected_result:
            self.add_pass_message(grades)             
        else:
            self.add_fail_messages(grades, 
                ["Did not receive expected response from recv_until_delimiter"])
            passing_all = False                     
            
        grades.add_message("Testing recv_until_delimiter (multiple)...")
        sock.sendall(b"\n")
        
        for i in range(10):
            result = client.recv_until_delimiter(b"\n")
            expected_result = b"NEW LINES" * 16 * (i+1)
            if result != expected_result:
                self.add_fail_messages(grades, 
                    ["Did not receive expected response from recv_until_delimiter"])
                passing_all = False      
                break
        else:
            self.add_pass_message(grades)             
       
        client.close()        
        return passing_all        

class UploadTest(Lab3Test):

    def execute_helper(self, grades, client, ex):
        passing_all = True
        
        for path in self.good_files:
            grades.add_message("Testing uploading " + path + "...")
            try:
                client.upload_file(path)
            except ex:
                self.add_fail_messages(grades, ["Error on uploading " + path])
                passing_all = False
            else:
                self.add_pass_message(grades)
       
        for path in self.bad_files:
            grades.add_message("Testing uploading " + path + "...")
            try:
                client.upload_file(path)
            except ex:
                self.add_pass_message(grades)
            else:
                self.add_fail_messages(grades, 
                        ["No UploadError on uploading " + path + 
                         ", but there should be"])
                passing_all = False
                
        
        return passing_all
       
    def execute(self, grades, module_dict, solution_dict):            
        upload_client = module_dict["upload_client"]        
        client = upload_client.UploadClient(HOST, UPLOAD_PORT)
        passing_all = self.execute_helper(grades, client, upload_client.UploadError)
        client.close()        
        return passing_all
        
        
class ListTest(UploadTest):

    def execute(self, grades, module_dict, solution_dict):            
        upload_client = module_dict["upload_client"]        
        client = upload_client.UploadClient(HOST, UPLOAD_PORT)
        passing_all = self.execute_helper(grades, client, upload_client.UploadError)
        
        
        
        uploaded_files = client.list_files()
        
        client.close()
        
        if len(uploaded_files) != len(self.good_files):
            self.add_fail_messages(grades, 
                        ["Incorrect number of results returned.", 
                         "Returned {}, but should have been {}".format(
                            len(uploaded_files), len(self.good_files))])
            return False

        for path, result in zip(self.good_files, uploaded_files):
            if len(result) != 2:
                self.add_fail_messages(grades, 
                        ["Should be receiving a list of 2-tuples"])
                return False
                                
            file_name = os.path.basename(path)
            if file_name != result[0]:
                self.add_fail_messages(grades, 
                        ["File names not matching.", 
                         "Returned {}, but should have been {}".format(
                            result[0], file_name)])
                passing_all = False
                
            with open(path,"rb") as f:
                size = len(f.read())
                if size != result[1]:
                    self.add_fail_messages(grades, 
                        ["File sizes not matching.", 
                         "Returned {}, but should have been {}".format(
                            result[1], size)])
                    passing_all = False

        if passing_all:
            self.add_pass_message(grades)

        return passing_all
                                    
       
            

