import React from 'react';
import { useParams } from 'react-router-dom';
import { LogDetail } from '@lumina/data-hub';

const LogDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  if (!id) {
    return <div>Log ID not provided</div>;
  }

  return <LogDetail logId={id} />;
};

export default LogDetailPage;
