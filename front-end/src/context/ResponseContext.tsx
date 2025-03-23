
'use client'

import React, { useState, createContext, ReactNode, useContext } from "react";

export type Response = {
    id: String;
    single_choice: number;
}

type ResponseContextType = {
    responses: Response[] | null;
    setResponses: (id: Response[] | null) => void 
};

export const ResponseContext = createContext<ResponseContextType | undefined>(undefined);

export const ResponseProvider: React.FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [responses, setResponses] = useState<Response[] | null>(null);

    return (
        <ResponseContext.Provider
          value={{
            responses,
            setResponses
          }}
        >
          {children}
        </ResponseContext.Provider>
      );
}

export const useResponse = () => {
  const context = useContext(ResponseContext);
  if (!context) {
    throw new Error("useResponse must be used within a CourseProvider");
  }
  return context;
};
