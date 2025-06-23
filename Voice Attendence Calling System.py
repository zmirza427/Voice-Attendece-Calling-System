import json
import os
import pyttsx3
import time
from datetime import datetime
from typing import Dict, List

class VoiceAttendanceSystem:
    def __init__(self, data_file='attendance_data.json'):
        self.data_file = data_file
        self.students = {}
        self.attendance_records = {}
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.setup_voice()
        self.load_data()
    
    def setup_voice(self):
        """Configure the text-to-speech engine"""
        voices = self.tts_engine.getProperty('voices')
        
        # Try to set a female voice if available
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                self.tts_engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"🔊 Speaking: {text}")
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def load_data(self):
        """Load existing data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.students = data.get('students', {})
                    self.attendance_records = data.get('attendance_records', {})
            except (json.JSONDecodeError, FileNotFoundError):
                self.students = {}
                self.attendance_records = {}
    
    def save_data(self):
        """Save data to file"""
        data = {
            'students': self.students,
            'attendance_records': self.attendance_records
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_student(self, student_id: str, name: str):
        """Add a new student to the system"""
        if student_id in self.students:
            message = f"Student with ID {student_id} already exists!"
            print(message)
            self.speak(message)
            return False
        
        self.students[student_id] = {
            'name': name,
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self.save_data()
        message = f"Student {name} with ID {student_id} added successfully!"
        print(message)
        self.speak(message)
        return True
    
    def voice_attendance_call(self, date: str = None, delay: int = 3):
        """Call attendance using voice with customizable delay"""
        if not self.students:
            message = "No students registered in the system!"
            print(message)
            self.speak(message)
            return
        
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date in self.attendance_records:
            message = f"Attendance for {date} already exists!"
            print(message)
            self.speak(message)
            choice = input("Do you want to update it? (y/n): ").lower()
            if choice != 'y':
                return
        
        # Start attendance session
        start_message = f"Starting attendance call for {date}. Please respond with present, absent, or late after each name is called."
        print(f"\n--- {start_message} ---")
        self.speak(start_message)
        time.sleep(2)
        
        self.attendance_records[date] = {}
        
        for student_id, student_info in self.students.items():
            student_name = student_info['name']
            
            # Call student's name
            call_message = f"Calling {student_name}"
            print(f"\n🎯 {call_message}")
            self.speak(call_message)
            
            # Wait for response
            time.sleep(1)
            while True:
                print("Enter response: 'p' for Present, 'a' for Absent, 'l' for Late, 'r' to repeat name")
                response = input(f"Response for {student_name}: ").lower().strip()
                
                if response == 'r':
                    self.speak(student_name)
                    continue
                elif response in ['p', 'a', 'l']:
                    status_map = {'p': 'Present', 'a': 'Absent', 'l': 'Late'}
                    status = status_map[response]
                    
                    self.attendance_records[date][student_id] = {
                        'status': status,
                        'marked_time': datetime.now().strftime('%H:%M:%S')
                    }
                    
                    # Confirm the status
                    confirm_message = f"{student_name} marked as {status}"
                    print(f"✓ {confirm_message}")
                    self.speak(confirm_message)
                    break
                else:
                    error_msg = "Invalid input! Please enter p, a, l, or r"
                    print(error_msg)
                    self.speak(error_msg)
            
            # Delay before next student (except for the last one)
            if student_id != list(self.students.keys())[-1]:
                time.sleep(delay)
        
        self.save_data()
        completion_message = f"Attendance call completed for {date}"
        print(f"\n✅ {completion_message}")
        self.speak(completion_message)
    
    def quick_attendance_call(self, date: str = None):
        """Quick attendance call with minimal delays"""
        self.voice_attendance_call(date, delay=1)
    
    def detailed_attendance_call(self, date: str = None):
        """Detailed attendance call with longer delays for large classes"""
        self.voice_attendance_call(date, delay=5)
    
    def announce_attendance_summary(self, date: str = None):
        """Announce attendance summary using voice"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date not in self.attendance_records:
            message = f"No attendance records found for {date}"
            print(message)
            self.speak(message)
            return
        
        records = self.attendance_records[date]
        present_count = sum(1 for r in records.values() if r['status'] == 'Present')
        absent_count = sum(1 for r in records.values() if r['status'] == 'Absent')
        late_count = sum(1 for r in records.values() if r['status'] == 'Late')
        total_count = len(records)
        
        summary = f"Attendance summary for {date}. Total students: {total_count}. Present: {present_count}. Absent: {absent_count}. Late: {late_count}."
        
        print(f"\n📊 {summary}")
        self.speak(summary)
        
        # Announce absent students if any
        if absent_count > 0:
            absent_students = [self.students[sid]['name'] for sid, record in records.items() 
                             if record['status'] == 'Absent' and sid in self.students]
            if absent_students:
                absent_message = f"Absent students are: {', '.join(absent_students)}"
                print(f"❌ {absent_message}")
                self.speak(absent_message)
    
    def call_individual_student(self, student_id: str):
        """Call a specific student's name"""
        if student_id not in self.students:
            message = f"Student with ID {student_id} not found!"
            print(message)
            self.speak(message)
            return
        
        student_name = self.students[student_id]['name']
        message = f"Calling {student_name}"
        print(message)
        self.speak(message)
    
    def test_voice(self):
        """Test the voice system"""
        test_message = "Voice system is working correctly. This is a test announcement."
        print(test_message)
        self.speak(test_message)
    
    def change_voice_settings(self):
        """Change voice speed and volume settings"""
        print("\n--- Voice Settings ---")
        current_rate = self.tts_engine.getProperty('rate')
        current_volume = self.tts_engine.getProperty('volume')
        
        print(f"Current speech rate: {current_rate}")
        print(f"Current volume: {current_volume}")
        
        try:
            new_rate = input(f"Enter new speech rate (50-300, current: {current_rate}): ").strip()
            if new_rate:
                rate = int(new_rate)
                if 50 <= rate <= 300:
                    self.tts_engine.setProperty('rate', rate)
                    self.speak(f"Speech rate changed to {rate}")
                else:
                    print("Rate must be between 50 and 300")
            
            new_volume = input(f"Enter new volume (0.0-1.0, current: {current_volume}): ").strip()
            if new_volume:
                volume = float(new_volume)
                if 0.0 <= volume <= 1.0:
                    self.tts_engine.setProperty('volume', volume)
                    self.speak(f"Volume changed to {volume}")
                else:
                    print("Volume must be between 0.0 and 1.0")
                    
        except ValueError:
            print("Invalid input! Please enter valid numbers.")
    
    def view_attendance(self, date: str = None):
        """View attendance for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date not in self.attendance_records:
            print(f"No attendance records found for {date}")
            return
        
        print(f"\n--- Attendance Report for {date} ---")
        print(f"{'ID':<10} {'Name':<20} {'Status':<10} {'Time':<10}")
        print("-" * 50)
        
        for student_id, record in self.attendance_records[date].items():
            if student_id in self.students:
                name = self.students[student_id]['name']
                status = record['status']
                time = record['marked_time']
                print(f"{student_id:<10} {name:<20} {status:<10} {time:<10}")
    
    def list_students(self):
        """List all registered students"""
        if not self.students:
            print("No students registered!")
            return
        
        print("\n--- Registered Students ---")
        print(f"{'ID':<10} {'Name':<20} {'Added Date':<20}")
        print("-" * 50)
        
        for student_id, info in self.students.items():
            print(f"{student_id:<10} {info['name']:<20} {info['added_date']:<20}")

def main():
    print("Initializing Voice Attendance System...")
    system = VoiceAttendanceSystem()
    
    # Test voice on startup
    system.speak("Voice Attendance System initialized successfully")
    
    while True:
        print("\n" + "="*60)
        print("         🎤 VOICE ATTENDANCE CALLING SYSTEM 🎤")
        print("="*60)
        print("1. Add Student")
        print("2. Voice Attendance Call (Normal)")
        print("3. Quick Attendance Call")
        print("4. Detailed Attendance Call")
        print("5. Call Individual Student")
        print("6. Announce Attendance Summary")
        print("7. View Attendance Report")
        print("8. List All Students")
        print("9. Test Voice System")
        print("10. Change Voice Settings")
        print("11. Exit")
        print("-"*60)
        
        choice = input("Enter your choice (1-11): ").strip()
        
        if choice == '1':
            student_id = input("Enter Student ID: ").strip()
            name = input("Enter Student Name: ").strip()
            if student_id and name:
                system.add_student(student_id, name)
            else:
                print("Please provide both ID and name!")
        
        elif choice == '2':
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')
                    system.voice_attendance_call(date_input)
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD")
            else:
                system.voice_attendance_call()
        
        elif choice == '3':
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')
                    system.quick_attendance_call(date_input)
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD")
            else:
                system.quick_attendance_call()
        
        elif choice == '4':
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')
                    system.detailed_attendance_call(date_input)
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD")
            else:
                system.detailed_attendance_call()
        
        elif choice == '5':
            student_id = input("Enter Student ID to call: ").strip()
            if student_id:
                system.call_individual_student(student_id)
            else:
                print("Please provide Student ID!")
        
        elif choice == '6':
            date_input = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if date_input:
                try:
                    datetime.strptime(date_input, '%Y-%m-%d')
                    system.announce_attendance_summary(date_input)
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD")
            else:
                system.announce_attendance_summary()
        
        elif choice == '7':
            date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
            if not date:
                date = None
            elif date:
                try:
                    datetime.strptime(date, '%Y-%m-%d')
                except ValueError:
                    print("Invalid date format! Use YYYY-MM-DD")
                    continue
            system.view_attendance(date)
        
        elif choice == '8':
            system.list_students()
        
        elif choice == '9':
            system.test_voice()
        
        elif choice == '10':
            system.change_voice_settings()
        
        elif choice == '11':
            farewell_message = "Thank you for using the Voice Attendance System! Goodbye!"
            print(farewell_message)
            system.speak(farewell_message)
            break
        
        else:
            print("Invalid choice! Please enter a number between 1-11.")

if __name__ == "__main__":
    main()