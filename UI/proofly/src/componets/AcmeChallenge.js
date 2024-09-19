import React from 'react';
import { useParams } from 'react-router-dom';

function AcmeChallenge() {
  const { token } = useParams();

  // You can serve static content here based on the token
  // Typically, the content required for the SSL challenge would be hardcoded here.
  return (
    <div>
      ABCD HelloWorld
    </div>
  );
}

export default AcmeChallenge;
