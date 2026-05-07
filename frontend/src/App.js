import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/lib/auth";
import { Toaster } from "sonner";
import Welcome from "@/pages/Welcome";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Home from "@/pages/Home";
import Trail from "@/pages/Trail";
import Lesson from "@/pages/Lesson";
import Achievements from "@/pages/Achievements";
import Leaderboard from "@/pages/Leaderboard";
import Profile from "@/pages/Profile";
import Practice from "@/pages/Practice";
import AuthCallback from "@/pages/AuthCallback";
import Admin from "@/pages/Admin";
import Protected from "@/components/Protected";

function App() {
  return (
    <div className="App">
      <AuthProvider>
        <BrowserRouter>
          <Toaster richColors position="top-center" />
          <Routes>
            <Route path="/" element={<Welcome />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/home" element={<Protected><Home /></Protected>} />
            <Route path="/trail/:subjectId" element={<Protected><Trail /></Protected>} />
            <Route path="/lesson/:lessonId" element={<Protected><Lesson /></Protected>} />
            <Route path="/practice" element={<Protected><Practice /></Protected>} />
            <Route path="/achievements" element={<Protected><Achievements /></Protected>} />
            <Route path="/leaderboard" element={<Protected><Leaderboard /></Protected>} />
            <Route path="/profile" element={<Protected><Profile /></Protected>} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </div>
  );
}

export default App;