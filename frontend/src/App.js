import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Separator } from './components/ui/separator';
import { Avatar, AvatarFallback, AvatarImage } from './components/ui/avatar';
import { 
  BookOpen, 
  Calendar, 
  Users, 
  FileText, 
  Clock, 
  LogOut, 
  Bell,
  GraduationCap,
  MapPin,
  Mail,
  User,
  Home,
  Download
} from 'lucide-react';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loginData, setLoginData] = useState({ roll_no: '', password: '' });
  const [activeTab, setActiveTab] = useState('home');
  const [notices, setNotices] = useState([]);
  const [events, setEvents] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [faculty, setFaculty] = useState([]);
  const [resources, setResources] = useState([]);

  const API_BASE = process.env.REACT_APP_BACKEND_URL;

  // Check for existing token on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      fetchUserData(token);
    }
  }, []);

  const fetchUserData = async (token) => {
    try {
      const response = await axios.get(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUser(response.data);
      fetchAllData(token);
    } catch (error) {
      localStorage.removeItem('token');
      setUser(null);
    }
  };

  const fetchAllData = async (token) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [noticesRes, eventsRes, timetableRes, facultyRes, resourcesRes] = await Promise.all([
        axios.get(`${API_BASE}/api/notices`, { headers }),
        axios.get(`${API_BASE}/api/events`, { headers }),
        axios.get(`${API_BASE}/api/timetable`, { headers }),
        axios.get(`${API_BASE}/api/faculty`, { headers }),
        axios.get(`${API_BASE}/api/resources`, { headers })
      ]);
      
      setNotices(noticesRes.data);
      setEvents(eventsRes.data);
      setTimetable(timetableRes.data);
      setFaculty(facultyRes.data);
      setResources(resourcesRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, loginData);
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(userData);
      fetchAllData(access_token);
      setLoginData({ roll_no: '', password: '' });
    } catch (error) {
      alert('Login failed: ' + (error.response?.data?.detail || 'Please check your credentials'));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setNotices([]);
    setEvents([]);
    setTimetable([]);
    setFaculty([]);
    setResources([]);
    setActiveTab('home');
  };

  const groupTimetableByDay = (timetable) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days.reduce((acc, day) => {
      acc[day] = timetable.filter(entry => entry.day === day).sort((a, b) => a.time.localeCompare(b.time));
      return acc;
    }, {});
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <Card className="shadow-2xl border-0 bg-white/80 backdrop-blur-sm">
            <CardHeader className="text-center pb-2">
              <div className="mx-auto w-16 h-16 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center mb-4">
                <GraduationCap className="w-8 h-8 text-white" />
              </div>
              <CardTitle className="text-2xl font-bold text-gray-800 mb-2">Dept-AI Hub</CardTitle>
              <p className="text-sm text-gray-600 font-medium">PBR Vishnu Institute of Technology</p>
              <p className="text-xs text-gray-500">Artificial Intelligence Department</p>
            </CardHeader>
            <CardContent className="pt-6">
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="roll_no" className="text-sm font-medium text-gray-700">Roll Number</Label>
                  <Input
                    id="roll_no"
                    type="text"
                    placeholder="Enter your roll number"
                    value={loginData.roll_no}
                    onChange={(e) => setLoginData({...loginData, roll_no: e.target.value})}
                    required
                    className="mt-1 h-11"
                  />
                </div>
                <div>
                  <Label htmlFor="password" className="text-sm font-medium text-gray-700">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter your roll number as password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                    required
                    className="mt-1 h-11"
                  />
                </div>
                <Button 
                  type="submit" 
                  className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium"
                  disabled={loading}
                >
                  {loading ? 'Signing In...' : 'Sign In'}
                </Button>
              </form>
              <div className="mt-6 text-center">
                <p className="text-xs text-gray-500">Use your roll number as both username and password</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  const timetableByDay = groupTimetableByDay(timetable);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                <GraduationCap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-800">Dept-AI Hub</h1>
                <p className="text-xs text-gray-600">PBR VITS - AI Department</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm font-semibold text-gray-800">{user.name}</p>
                <p className="text-xs text-gray-600">{user.roll_no}</p>
                <p className="text-xs text-blue-600 font-medium">Class {user.semester} • Section {user.section}</p>
              </div>
              <Button 
                onClick={handleLogout}
                variant="ghost" 
                size="sm"
                className="text-gray-600 hover:text-red-600"
              >
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-6 bg-white/80 backdrop-blur-sm">
            <TabsTrigger value="home" className="flex items-center space-x-2">
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Home</span>
            </TabsTrigger>
            <TabsTrigger value="timetable" className="flex items-center space-x-2">
              <Clock className="w-4 h-4" />
              <span className="hidden sm:inline">Timetable</span>
            </TabsTrigger>
            <TabsTrigger value="notices" className="flex items-center space-x-2">
              <Bell className="w-4 h-4" />
              <span className="hidden sm:inline">Notices</span>
            </TabsTrigger>
            <TabsTrigger value="events" className="flex items-center space-x-2">
              <Calendar className="w-4 h-4" />
              <span className="hidden sm:inline">Events</span>
            </TabsTrigger>
            <TabsTrigger value="faculty" className="flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span className="hidden sm:inline">Faculty</span>
            </TabsTrigger>
            <TabsTrigger value="resources" className="flex items-center space-x-2">
              <BookOpen className="w-4 h-4" />
              <span className="hidden sm:inline">Resources</span>
            </TabsTrigger>
          </TabsList>

          {/* Home Tab */}
          <TabsContent value="home" className="space-y-6">
            <div className="text-center py-8">
              <h2 className="text-3xl font-bold text-gray-800 mb-2">Welcome back, {user.name}!</h2>
              <div className="text-gray-600 space-y-1">
                <p className="text-lg">Roll Number: <span className="font-semibold text-blue-600">{user.roll_no}</span></p>
                <p className="text-lg">Class: <span className="font-semibold text-blue-600">{user.semester}</span> • Section: <span className="font-semibold text-blue-600">{user.section}</span></p>
                <p className="text-sm mt-3">Stay updated with department activities and academics</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100">Total Notices</p>
                      <p className="text-2xl font-bold">{notices.length}</p>
                    </div>
                    <Bell className="w-8 h-8 text-blue-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-indigo-500 to-indigo-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-indigo-100">Upcoming Events</p>
                      <p className="text-2xl font-bold">{events.length}</p>
                    </div>
                    <Calendar className="w-8 h-8 text-indigo-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100">Faculty Members</p>
                      <p className="text-2xl font-bold">{faculty.length}</p>
                    </div>
                    <Users className="w-8 h-8 text-purple-200" />
                  </div>
                </CardContent>
              </Card>
              
              <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100">Resources</p>
                      <p className="text-2xl font-bold">{resources.length}</p>
                    </div>
                    <BookOpen className="w-8 h-8 text-green-200" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Notices */}
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="w-5 h-5" />
                  <span>Recent Notices</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {notices.slice(0, 3).map((notice, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 rounded-lg bg-blue-50">
                      <Badge variant="secondary" className="mt-1">{notice.category}</Badge>
                      <div className="flex-1">
                        <h4 className="font-semibold text-gray-800">{notice.title}</h4>
                        <p className="text-sm text-gray-600 mt-1">{notice.description}</p>
                        <p className="text-xs text-gray-500 mt-2">{notice.date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Timetable Tab */}
          <TabsContent value="timetable" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Weekly Timetable - Semester {user.semester}, Section {user.section}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {Object.entries(timetableByDay).map(([day, classes]) => (
                    <div key={day} className="border rounded-lg p-4 bg-gray-50">
                      <h3 className="font-semibold text-lg mb-3 text-gray-800">{day}</h3>
                      {classes.length > 0 ? (
                        <div className="space-y-2">
                          {classes.map((class_entry, index) => (
                            <div key={index} className="bg-white p-3 rounded border-l-4 border-blue-500">
                              <div className="flex justify-between items-start">
                                <div>
                                  <p className="font-semibold text-gray-800">{class_entry.subject}</p>
                                  <p className="text-sm text-gray-600">{class_entry.faculty}</p>
                                </div>
                                <Badge variant="outline">{class_entry.time}</Badge>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-gray-500 text-sm">No classes scheduled</p>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Notices Tab */}
          <TabsContent value="notices" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Bell className="w-5 h-5" />
                  <span>Department Notices</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {notices.map((notice, index) => (
                    <div key={index} className="border rounded-lg p-4 bg-gray-50">
                      <div className="flex items-start justify-between mb-2">
                        <Badge variant="secondary">{notice.category}</Badge>
                        <p className="text-sm text-gray-500">{notice.date}</p>
                      </div>
                      <h3 className="font-semibold text-lg text-gray-800 mb-2">{notice.title}</h3>
                      <p className="text-gray-600">{notice.description}</p>
                      {notice.pdf_url && (
                        <Button variant="outline" size="sm" className="mt-3">
                          <Download className="w-4 h-4 mr-2" />
                          Download PDF
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Events Tab */}
          <TabsContent value="events" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="w-5 h-5" />
                  <span>Upcoming Events</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {events.map((event, index) => (
                    <div key={index} className="border rounded-lg p-4 bg-gradient-to-br from-blue-50 to-indigo-50">
                      <h3 className="font-semibold text-lg text-gray-800 mb-2">{event.title}</h3>
                      <p className="text-gray-600 mb-3">{event.description}</p>
                      <div className="space-y-2">
                        <div className="flex items-center text-sm text-gray-600">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{event.date}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin className="w-4 h-4 mr-2" />
                          <span>{event.location}</span>
                        </div>
                      </div>
                      {event.rsvp_link && (
                        <Button variant="outline" size="sm" className="mt-3">
                          Register Now
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Faculty Tab */}
          <TabsContent value="faculty" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5" />
                  <span>Faculty Directory</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {faculty.map((member, index) => (
                    <div key={index} className="text-center p-6 border rounded-lg bg-gradient-to-br from-gray-50 to-blue-50">
                      <Avatar className="w-20 h-20 mx-auto mb-4">
                        <AvatarImage src={member.photo_url} alt={member.name} />
                        <AvatarFallback className="text-lg bg-blue-100 text-blue-600">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </AvatarFallback>
                      </Avatar>
                      <h3 className="font-semibold text-lg text-gray-800">{member.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{member.designation}</p>
                      <div className="flex items-center justify-center text-sm text-gray-600">
                        <Mail className="w-4 h-4 mr-2" />
                        <span>{member.email}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Resources Tab */}
          <TabsContent value="resources" className="space-y-6">
            <Card className="bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BookOpen className="w-5 h-5" />
                  <span>Academic Resources - Semester {user.semester}</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {resources.length > 0 ? (
                  <div className="space-y-4">
                    {resources.map((resource, index) => (
                      <div key={index} className="border rounded-lg p-4 bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg text-gray-800">{resource.title}</h3>
                            <p className="text-sm text-gray-600">Subject: {resource.subject}</p>
                            <p className="text-xs text-gray-500 mt-1">Uploaded by: {resource.uploaded_by}</p>
                          </div>
                          <Button variant="outline" size="sm">
                            <Download className="w-4 h-4 mr-2" />
                            Download
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No resources available for your semester yet.</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;