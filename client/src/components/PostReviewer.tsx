import React, { useState } from 'react';

type Platform = 'LinkedIn' | 'Instagram' | 'Twitter' | 'Facebook';
const platforms: Platform[] = ['LinkedIn', 'Instagram', 'Twitter', 'Facebook'];

interface Limitations {
  char_limit?: number;
  hashtag_limit?: number;
}

interface ReviewResult {
  tone: string;
  limitations: Limitations;
  suggestions: string;
  revised_post: string;
}

const PostReviewer: React.FC = () => {
  const [text, setText] = useState<string>('');
  const [platform, setPlatform] = useState<Platform>(platforms[0]);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleReview = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, platform })
      });
      const data: ReviewResult = await response.json();
      setResult(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <textarea
        className="w-full border p-2 mb-2"
        rows={6}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Write your post here..."
      />

      <select
        className="border p-2 mb-2"
        value={platform}
        onChange={(e) => setPlatform(e.target.value as Platform)}
      >
        {platforms.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>

      <button
        className="bg-blue-600 text-white px-4 py-2 mb-4"
        onClick={handleReview}
        disabled={loading}
      >
        {loading ? 'Reviewing...' : 'Review Post'}
      </button>

      {result && (
        <div className="space-y-4">
          <div><strong>Tone:</strong> {result.tone}</div>
          <div>
            <strong>Limitations:</strong>{' '}
            Char Limit: {result.limitations.char_limit}, Hashtags: {result.limitations.hashtag_limit}
          </div>
          <div>
            <strong>Suggestions:</strong>
            <p>{result.suggestions}</p>
          </div>
          <div>
            <strong>Revised Post:</strong>
            <p>{result.revised_post}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PostReviewer;


