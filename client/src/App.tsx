import React from 'react';
import PostReviewer from './components/PostReviewer';

const App: React.FC = () => (
  <div className="p-4 max-w-xl mx-auto">
    <h1 className="text-2xl font-bold mb-4">Social Media Post Reviewer</h1>
    <PostReviewer />
  </div>
);

export default App;