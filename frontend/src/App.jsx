import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import NeuralBackground from './components/NeuralBackground/NeuralBackground';
import Header from './components/Header/Header';
import WelcomeScreen from './components/WelcomeScreen/WelcomeScreen';
import ChatWindow from './components/ChatWindow/ChatWindow';
import ChatInput from './components/ChatInput/ChatInput';
import { askQuestion } from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || isLoading) return;

    setMessages(prev => [...prev, { type: 'user', content: question }]);
    setInput('');
    setHasStarted(true);
    setIsLoading(true);

    try {
      const data = await askQuestion(question);
      setMessages(prev => [...prev, { type: 'ai', content: data }]);
    } catch (err) {
      const errorMsg = err?.message || "An unexpected error occurred. Please try again.";
      setMessages(prev => [
        ...prev,
        {
          type: 'ai',
          content: {
            summary: errorMsg,
            _isError: true,
          },
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      {/* Full-screen reactive neural canvas */}
      <NeuralBackground isThinking={isLoading} />

      {/* UI layer */}
      <div className="app-layer">
        {/* Header — shown once chat begins */}
        <AnimatePresence>
          {hasStarted && <Header key="header" isThinking={isLoading} />}
        </AnimatePresence>

        {/* Welcome → Chat transition */}
        <AnimatePresence mode="wait">
          {!hasStarted ? (
            <motion.div
              key="welcome"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, scale: 0.98 }}
              transition={{ duration: 0.3 }}
              className="app-view"
            >
              <WelcomeScreen
                input={input}
                setInput={setInput}
                onSend={handleSend}
                isLoading={isLoading}
              />
            </motion.div>
          ) : (
            <motion.div
              key="chat"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.25 }}
              className="app-view"
            >
              <ChatWindow messages={messages} isLoading={isLoading} />
              <ChatInput
                input={input}
                setInput={setInput}
                onSend={handleSend}
                isLoading={isLoading}
                placeholder="Ask about sales, deliveries, products…"
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default App;
