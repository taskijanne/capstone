import React, { useEffect, useState } from "react";
import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const App = () => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [query, setQuery] = useState("");
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);

  useEffect(() => {
    axios.get(`${API_URL}/models`)
      .then(response => {
        setModels(response.data.models || []);
        if (response.data.models.includes("custom t5-small")) {
          setSelectedModel("custom t5-small");
        }
      })
      .catch(err => console.error("Error fetching models:", err));
  }, []);

  const handleSearch = async () => {
    if (query.length < 5 || !selectedModel) {
      setError("Query must be at least 5 characters long and a model must be selected.");
      return;
    }
    setError("");

    try {
      const response = await axios.post(`${API_URL}/optimize_and_search`, {
        input: query,
        model: selectedModel
      });
      setResults(response.data);
    } catch (err) {
      setError("An error occurred while fetching search results.");
    }
  };

  return (
    <div className="container">
      <h1>Search Optimizer</h1>
      <input 
        type="text" 
        placeholder="Enter your search query" 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        className="input-field"
      />
      <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} className="dropdown">
        {models.map((model, idx) => (
          <option key={idx} value={model}>{model}</option>
        ))}
      </select>
      <button onClick={handleSearch} className="search-button">Optimize and Search</button>
      
      {error && <p className="error">{error}</p>}

      {results && results['optimized_query_results'] && results['original_query_results'] && (
        <div className="results-container">
          {['optimized_query_results', 'original_query_results'].map((key) => (
            <div key={key} className="result-column">
              <h2>{key === 'optimized_query_results' ? 'Optimized Query' : 'Original Query'}</h2>
              <h4>Query: {results[key].query}</h4> 
              { results[key].results.map((res, index) => (
                <div key={index} className="result-item">
                  <p><strong>Score:</strong> {res.score}</p>
                  {res.title && <p><strong>Title:</strong> {res.title}</p>}
                  {res.source_url && <p><strong>Source:</strong> <a href={res.source_url} target="_blank" rel="noopener noreferrer">{res.source_url}</a></p>}
                  <p>{res.data}</p>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default App;
