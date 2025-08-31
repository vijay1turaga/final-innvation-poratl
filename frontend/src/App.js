import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import axios from 'axios';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';
import './App.css';

// Import Lucide icons
import { 
  User, 
  Shield, 
  GraduationCap, 
  BookOpen, 
  Award, 
  TrendingUp, 
  Download,
  LogOut,
  Eye,
  EyeOff,
  Building2,
  Calendar,
  DollarSign,
  FileText,
  Users,
  BarChart3,
  Settings
} from 'lucide-react';

// Import UI components
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Label } from './components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Switch } from './components/ui/switch';
import { Textarea } from './components/ui/textarea';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userInfo = localStorage.getItem('userInfo');

    if (token && userInfo) {
      try {
        setUser(JSON.parse(userInfo));
      } catch (error) {
        console.error('Invalid userInfo in localStorage:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('userInfo');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password, userType) => {
    try {
      const response = await axios.post(`${API}/auth/login`, {
        email,
        password
      });
      
      if (response.data.user_type === userType) {
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('userInfo', JSON.stringify(response.data.user_info));
        setUser(response.data.user_info);
        return { success: true };
      } else {
        return { success: false, error: 'Invalid user type' };
      }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (email, password, fullName, userType) => {
    try {
      const response = await axios.post(`${API}/auth/register`, {
        email,
        password,
        full_name: fullName,
        user_type: userType
      });
      
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('userInfo', JSON.stringify(response.data.user_info));
      setUser(response.data.user_info);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// Auth hook
const useAuth = () => {
  return React.useContext(AuthContext);
};

// Axios interceptor for auth
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Landing Page
function LandingPage() {
  const [activeTab, setActiveTab] = useState('faculty');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Faculty IP Hub</h1>
                <p className="text-sm text-slate-600">Intellectual Property Management</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-5xl font-extrabold text-slate-800 mb-6 leading-tight">
            Manage Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-teal-500">Academic</span> Achievements
          </h2>
          <p className="text-xl text-slate-600 mb-12 max-w-3xl mx-auto">
            Streamline faculty intellectual property tracking, from Google Scholar metrics to patent commercialization data
          </p>
          
          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-blue-100">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Scholar Integration</h3>
              <p className="text-slate-600">Automatically sync your Google Scholar profile and research metrics</p>
            </div>
            
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-teal-100">
              <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-teal-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <Award className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Patent Tracking</h3>
              <p className="text-slate-600">Track patents, commercialization status, and revenue data</p>
            </div>
            
            <div className="bg-white p-8 rounded-2xl shadow-lg border border-orange-100">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mb-2">Analytics Dashboard</h3>
              <p className="text-slate-600">Comprehensive overview of academic and commercial impact</p>
            </div>
          </div>
        </div>
      </section>

      {/* Login Section */}
      <section className="py-16 px-4 bg-white">
        <div className="max-w-md mx-auto">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8">
              <TabsTrigger value="faculty" className="flex items-center gap-2">
                <User className="w-4 h-4" />
                Faculty
              </TabsTrigger>
              <TabsTrigger value="admin" className="flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Admin
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="faculty">
              <AuthForm userType="faculty" />
            </TabsContent>
            
            <TabsContent value="admin">
              <AuthForm userType="admin" />
            </TabsContent>
          </Tabs>
        </div>
      </section>
    </div>
  );
}

// Auth Form Component
function AuthForm({ userType }) {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    fullName: ''
  });

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      let result;
      if (isLogin || userType === 'admin') {
        // Admin can only login, no registration
        result = await login(formData.email, formData.password, userType);
      } else {
        // Only faculty can register
        result = await register(formData.email, formData.password, formData.fullName, userType);
      }

      if (result.success) {
        toast.success(isLogin || userType === 'admin' ? 'Login successful!' : 'Account created successfully!');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full shadow-xl border-0 bg-gradient-to-br from-white to-blue-50">
      <CardHeader className="text-center pb-2">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-blue-600 to-teal-500 rounded-2xl flex items-center justify-center">
          {userType === 'admin' ? (
            <Shield className="w-8 h-8 text-white" />
          ) : (
            <User className="w-8 h-8 text-white" />
          )}
        </div>
        <CardTitle className="text-2xl font-bold text-slate-800">
          {userType === 'admin' ? 'Admin Access' : 'Faculty Portal'}
        </CardTitle>
        <p className="text-slate-600 mt-2">
          {isLogin ? 'Sign in to your account' : 'Create your account'}
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && userType === 'faculty' && (
            <div className="space-y-2">
              <Label htmlFor="fullName">Full Name</Label>
              <Input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                required={!isLogin && userType === 'faculty'}
                className="border-slate-300 focus:border-blue-500"
              />
            </div>
          )}
          
          <div className="space-y-2">
            <Label htmlFor="email">{userType === 'admin' ? 'Admin Email' : 'Email'}</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              required
              className="border-slate-300 focus:border-blue-500"
              placeholder={userType === 'admin' ? 'Admin Email' : 'Enter your email'}
              autoComplete="username"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                value={formData.password}
                onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                required
                className="border-slate-300 focus:border-blue-500 pr-10"
                placeholder={userType === 'admin' ? 'Password' : 'Enter your password'}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
          
          {userType === 'admin' && (
            <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
              <p className="text-sm text-blue-800">
                <strong>Admin Access:</strong> Use the official NIT admin credentials to login.
              </p>
            </div>
          )}
          
          <Button 
            type="submit" 
            className="w-full bg-gradient-to-r from-blue-600 to-teal-500 hover:from-blue-700 hover:to-teal-600"
            disabled={loading}
          >
            {loading ? 'Processing...' : (userType === 'admin' ? 'Admin Login' : (isLogin ? 'Sign In' : 'Create Account'))}
          </Button>
        </form>
        
        {userType === 'faculty' && (
          <div className="text-center">
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        )}
        
        {userType === 'admin' && (
          <div className="text-center">
            <p className="text-sm text-slate-600">
              Admin registration is not allowed. Use official credentials only.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Faculty Dashboard
function FacultyDashboard() {
  const { user, logout } = useAuth();
  const [patents, setPatents] = useState([]);
  const [scholarData, setScholarData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [scholarUrl, setScholarUrl] = useState('');
  const [patentForm, setPatentForm] = useState({
    title: '',
    date_issued: '',
    patent_number: '',
    commercialized: false,
    commercialization_amount: ''
  });

  useEffect(() => {
    loadPatents();
    if (user?.scholar_data) {
      setScholarData(user.scholar_data);
    }
  }, [user]);

  const loadPatents = async () => {
    try {
      const response = await axios.get(`${API}/faculty/patents`);
      setPatents(response.data);
    } catch (error) {
      toast.error('Failed to load patents');
    }
  };

  const updateScholarProfile = async () => {
    if (!scholarUrl.trim()) {
      toast.error('Please enter a valid Google Scholar URL');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.put(`${API}/faculty/scholar`, {
        google_scholar_url: scholarUrl
      });
      setScholarData(response.data.data);
      toast.success('Google Scholar profile updated successfully!');
    } catch (error) {
      toast.error('Failed to update Google Scholar profile');
    } finally {
      setLoading(false);
    }
  };

  const addPatent = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const patentData = {
        ...patentForm,
        commercialization_amount: patentForm.commercialized && patentForm.commercialization_amount 
          ? parseFloat(patentForm.commercialization_amount) 
          : null
      };
      
      await axios.post(`${API}/faculty/patents`, patentData);
      toast.success('Patent added successfully!');
      setPatentForm({
        title: '',
        date_issued: '',
        patent_number: '',
        commercialized: false,
        commercialization_amount: ''
      });
      loadPatents();
    } catch (error) {
      toast.error('Failed to add patent');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-blue-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Faculty Dashboard</h1>
                <p className="text-sm text-slate-600">Welcome back, {user?.full_name}</p>
              </div>
            </div>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="scholar">Google Scholar</TabsTrigger>
            <TabsTrigger value="patents">Patents</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100 text-sm font-medium">Total Patents</p>
                      <p className="text-3xl font-bold">{patents.length}</p>
                    </div>
                    <Award className="w-8 h-8 text-blue-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-teal-500 to-teal-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-teal-100 text-sm font-medium">Commercialized</p>
                      <p className="text-3xl font-bold">{patents.filter(p => p.commercialized).length}</p>
                    </div>
                    <TrendingUp className="w-8 h-8 text-teal-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-orange-500 to-orange-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-orange-100 text-sm font-medium">Total Citations</p>
                      <p className="text-3xl font-bold">{scholarData?.citations?.total || '0'}</p>
                    </div>
                    <BookOpen className="w-8 h-8 text-orange-200" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100 text-sm font-medium">H-Index</p>
                      <p className="text-3xl font-bold">{scholarData?.citations?.h_index || '0'}</p>
                    </div>
                    <BarChart3 className="w-8 h-8 text-purple-200" />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
              </CardHeader>
              <CardContent>
                {patents.length > 0 ? (
                  <div className="space-y-4">
                    {patents.slice(0, 3).map((patent) => (
                      <div key={patent.id} className="flex items-center justify-between p-4 bg-slate-50 rounded-lg">
                        <div>
                          <p className="font-medium text-slate-800">{patent.title}</p>
                          <p className="text-sm text-slate-600">Issued: {patent.date_issued}</p>
                        </div>
                        <Badge variant={patent.commercialized ? "default" : "secondary"}>
                          {patent.commercialized ? 'Commercialized' : 'Not Commercialized'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-600 text-center py-8">No patents added yet. Add your first patent in the Patents tab.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Google Scholar Tab */}
          <TabsContent value="scholar" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Google Scholar Integration</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Input
                    placeholder="Enter your Google Scholar profile URL"
                    value={scholarUrl}
                    onChange={(e) => setScholarUrl(e.target.value)}
                    className="flex-1"
                  />
                  <Button onClick={updateScholarProfile} disabled={loading}>
                    {loading ? 'Updating...' : 'Update Profile'}
                  </Button>
                </div>

                {scholarData && (
                  <div className="grid md:grid-cols-2 gap-6 mt-6">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Profile Information</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-center gap-3">
                          <Building2 className="w-5 h-5 text-slate-600" />
                          <div>
                            <p className="font-medium">{scholarData.name}</p>
                            <p className="text-sm text-slate-600">{scholarData.affiliation}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Citation Metrics</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <p className="text-2xl font-bold text-blue-600">{scholarData.citations?.total || '0'}</p>
                            <p className="text-xs text-slate-600">Citations</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-teal-600">{scholarData.citations?.h_index || '0'}</p>
                            <p className="text-xs text-slate-600">H-Index</p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-orange-600">{scholarData.citations?.i10_index || '0'}</p>
                            <p className="text-xs text-slate-600">i10-Index</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {scholarData.publications && scholarData.publications.length > 0 && (
                      <Card className="md:col-span-2">
                        <CardHeader>
                          <CardTitle className="text-lg">Recent Publications</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            {scholarData.publications.map((pub, index) => (
                              <div key={index} className="border-l-4 border-blue-500 pl-4">
                                <p className="font-medium text-slate-800">{pub.title}</p>
                                <p className="text-sm text-slate-600">{pub.authors}</p>
                                <div className="flex items-center gap-4 mt-1">
                                  <span className="text-xs text-slate-500 flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    {pub.year}
                                  </span>
                                  <span className="text-xs text-slate-500">{pub.citations} citations</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Patents Tab */}
          <TabsContent value="patents" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Add New Patent</CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={addPatent} className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">Patent Title</Label>
                      <Input
                        id="title"
                        value={patentForm.title}
                        onChange={(e) => setPatentForm(prev => ({ ...prev, title: e.target.value }))}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="date_issued">Date Issued</Label>
                      <Input
                        id="date_issued"
                        type="date"
                        value={patentForm.date_issued}
                        onChange={(e) => setPatentForm(prev => ({ ...prev, date_issued: e.target.value }))}
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="patent_number">Patent Number (Optional)</Label>
                    <Input
                      id="patent_number"
                      value={patentForm.patent_number}
                      onChange={(e) => setPatentForm(prev => ({ ...prev, patent_number: e.target.value }))}
                    />
                  </div>

                  <div className="flex items-center space-x-3">
                    <Switch
                      id="commercialized"
                      checked={patentForm.commercialized}
                      onCheckedChange={(checked) => setPatentForm(prev => ({ ...prev, commercialized: checked }))}
                    />
                    <Label htmlFor="commercialized">Commercialized</Label>
                  </div>

                  {patentForm.commercialized && (
                    <div className="space-y-2">
                      <Label htmlFor="amount">Commercialization Amount ($)</Label>
                      <Input
                        id="amount"
                        type="number"
                        step="0.01"
                        value={patentForm.commercialization_amount}
                        onChange={(e) => setPatentForm(prev => ({ ...prev, commercialization_amount: e.target.value }))}
                      />
                    </div>
                  )}

                  <Button type="submit" disabled={loading} className="w-full">
                    {loading ? 'Adding...' : 'Add Patent'}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Patents List */}
            <Card>
              <CardHeader>
                <CardTitle>Your Patents</CardTitle>
              </CardHeader>
              <CardContent>
                {patents.length > 0 ? (
                  <div className="space-y-4">
                    {patents.map((patent) => (
                      <div key={patent.id} className="p-6 border border-slate-200 rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h3 className="font-semibold text-slate-800 mb-2">{patent.title}</h3>
                            <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                              <div className="flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Issued: {patent.date_issued}
                              </div>
                              {patent.patent_number && (
                                <div className="flex items-center gap-2">
                                  <FileText className="w-4 h-4" />
                                  Patent #: {patent.patent_number}
                                </div>
                              )}
                              {patent.commercialized && patent.commercialization_amount && (
                                <div className="flex items-center gap-2">
                                  <DollarSign className="w-4 h-4" />
                                  Revenue: ${patent.commercialization_amount.toLocaleString()}
                                </div>
                              )}
                            </div>
                          </div>
                          <Badge variant={patent.commercialized ? "default" : "secondary"}>
                            {patent.commercialized ? 'Commercialized' : 'Not Commercialized'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-slate-600 text-center py-8">No patents added yet.</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

// Admin Dashboard
function AdminDashboard() {
  const { logout } = useAuth();
  const [faculty, setFaculty] = useState([]);
  const [selectedFaculty, setSelectedFaculty] = useState(null);
  const [facultyPatents, setFacultyPatents] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFaculty();
  }, []);

  const loadFaculty = async () => {
    try {
      const response = await axios.get(`${API}/admin/faculty`);
      setFaculty(response.data);
    } catch (error) {
      toast.error('Failed to load faculty data');
    }
  };

  const loadFacultyPatents = async (facultyId) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/admin/faculty/${facultyId}/patents`);
      setFacultyPatents(response.data);
    } catch (error) {
      toast.error('Failed to load faculty patents');
    } finally {
      setLoading(false);
    }
  };

  const exportFacultyData = async (facultyId) => {
    try {
      const response = await axios.get(`${API}/admin/faculty/${facultyId}/export`);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `faculty_${facultyId}_export.json`;
      link.click();
      URL.revokeObjectURL(url);
      toast.success('Faculty data exported successfully');
    } catch (error) {
      toast.error('Failed to export faculty data');
    }
  };

  const viewFacultyDetails = (faculty) => {
    setSelectedFaculty(faculty);
    loadFacultyPatents(faculty.id);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Admin Dashboard</h1>
                <p className="text-sm text-slate-600">Faculty Management & Analytics</p>
              </div>
            </div>
            <Button onClick={logout} variant="outline" size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Logout
            </Button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!selectedFaculty ? (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-slate-800">Faculty Overview</h2>
              <div className="text-sm text-slate-600">
                Total Faculty: {faculty.length}
              </div>
            </div>

            <div className="grid gap-6">
              {faculty.map((member) => (
                <Card key={member.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-teal-500 rounded-full flex items-center justify-center">
                          <User className="w-6 h-6 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-slate-800">{member.full_name}</h3>
                          <p className="text-slate-600">{member.email}</p>
                          {member.scholar_data?.affiliation && (
                            <p className="text-sm text-slate-500">{member.scholar_data.affiliation}</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          onClick={() => viewFacultyDetails(member)}
                          variant="outline"
                          size="sm"
                        >
                          View Details
                        </Button>
                        <Button
                          onClick={() => exportFacultyData(member.id)}
                          variant="outline"
                          size="sm"
                        >
                          <Download className="w-4 h-4 mr-2" />
                          Export
                        </Button>
                      </div>
                    </div>
                    
                    {member.scholar_data?.citations && (
                      <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t border-slate-200">
                        <div className="text-center">
                          <p className="text-lg font-semibold text-blue-600">{member.scholar_data.citations.total || '0'}</p>
                          <p className="text-xs text-slate-600">Citations</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-semibold text-teal-600">{member.scholar_data.citations.h_index || '0'}</p>
                          <p className="text-xs text-slate-600">H-Index</p>
                        </div>
                        <div className="text-center">
                          <p className="text-lg font-semibold text-orange-600">{member.scholar_data.citations.i10_index || '0'}</p>
                          <p className="text-xs text-slate-600">i10-Index</p>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {faculty.length === 0 && (
              <Card>
                <CardContent className="py-12 text-center">
                  <Users className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-slate-600">No faculty members registered yet.</p>
                </CardContent>
              </Card>
            )}
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <Button
                onClick={() => setSelectedFaculty(null)}
                variant="outline"
                size="sm"
              >
                ← Back to Faculty List
              </Button>
              <Button
                onClick={() => exportFacultyData(selectedFaculty.id)}
                variant="outline"
                size="sm"
              >
                <Download className="w-4 h-4 mr-2" />
                Export Data
              </Button>
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-teal-500 rounded-full flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                  {selectedFaculty.full_name}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-slate-800 mb-2">Contact Information</h4>
                    <p className="text-slate-600">{selectedFaculty.email}</p>
                  </div>
                  {selectedFaculty.scholar_data && (
                    <div>
                      <h4 className="font-medium text-slate-800 mb-2">Affiliation</h4>
                      <p className="text-slate-600">{selectedFaculty.scholar_data.affiliation}</p>
                    </div>
                  )}
                </div>

                {selectedFaculty.scholar_data?.citations && (
                  <div>
                    <h4 className="font-medium text-slate-800 mb-4">Citation Metrics</h4>
                    <div className="grid grid-cols-3 gap-4">
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-blue-600">{selectedFaculty.scholar_data.citations.total || '0'}</p>
                          <p className="text-sm text-slate-600">Total Citations</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-teal-600">{selectedFaculty.scholar_data.citations.h_index || '0'}</p>
                          <p className="text-sm text-slate-600">H-Index</p>
                        </CardContent>
                      </Card>
                      <Card>
                        <CardContent className="p-4 text-center">
                          <p className="text-2xl font-bold text-orange-600">{selectedFaculty.scholar_data.citations.i10_index || '0'}</p>
                          <p className="text-sm text-slate-600">i10-Index</p>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                )}

                <div>
                  <h4 className="font-medium text-slate-800 mb-4">Patents</h4>
                  {loading ? (
                    <p className="text-slate-600">Loading patents...</p>
                  ) : facultyPatents.length > 0 ? (
                    <div className="space-y-4">
                      {facultyPatents.map((patent) => (
                        <Card key={patent.id}>
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <h5 className="font-medium text-slate-800 mb-2">{patent.title}</h5>
                                <div className="grid grid-cols-2 gap-4 text-sm text-slate-600">
                                  <div className="flex items-center gap-2">
                                    <Calendar className="w-4 h-4" />
                                    Issued: {patent.date_issued}
                                  </div>
                                  {patent.patent_number && (
                                    <div className="flex items-center gap-2">
                                      <FileText className="w-4 h-4" />
                                      Patent #: {patent.patent_number}
                                    </div>
                                  )}
                                  {patent.commercialized && patent.commercialization_amount && (
                                    <div className="flex items-center gap-2">
                                      <DollarSign className="w-4 h-4" />
                                      Revenue: ${patent.commercialization_amount.toLocaleString()}
                                    </div>
                                  )}
                                </div>
                              </div>
                              <Badge variant={patent.commercialized ? "default" : "secondary"}>
                                {patent.commercialized ? 'Commercialized' : 'Not Commercialized'}
                              </Badge>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-600">No patents added yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}

// Main App Component
function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4 animate-pulse">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={
            !user ? <LandingPage /> : 
            user.user_type === 'faculty' ? <Navigate to="/faculty" replace /> :
            <Navigate to="/admin" replace />
          } />
          <Route path="/faculty" element={
            user?.user_type === 'faculty' ? <FacultyDashboard /> : <Navigate to="/" replace />
          } />
          <Route path="/admin" element={
            user?.user_type === 'admin' ? <AdminDashboard /> : <Navigate to="/" replace />
          } />
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}