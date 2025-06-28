import React from 'react';
import PostReviewer from './components/PostReviewer';

const App: React.FC = () => (
  <div className="app-container">
    <h1 className="title">Social Media Post Reviewer</h1>
    <PostReviewer />
  </div>
);

export default App;