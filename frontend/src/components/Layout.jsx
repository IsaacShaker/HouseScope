import Navigation from './Navigation';

const Layout = ({ children }) => {
  return (
    <div style={{ display: 'flex', width: '100vw', minHeight: '100vh' }}>
      {/* Sidebar Navigation */}
      <Navigation />
      
      {/* Main Content Area */}
      <div style={{ 
        display: 'flex', 
        flexDirection: 'column',
        width: '100%',
        padding: '20px',
        paddingLeft: '20px',
        overflowY: 'auto',
        backgroundColor: '#f9fafb'
      }}>
        {children}
      </div>
    </div>
  );
};

export default Layout;
