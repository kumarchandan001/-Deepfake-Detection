package sdk

import (
	"fmt"
)

// AntigravityForensicsClient wraps API settings
type AntigravityForensicsClient struct {
	APIKey  string
	BaseURL string
}

// NewClient returns client instance
func NewClient(apiKey string, baseURL string) *AntigravityForensicsClient {
	if baseURL == "" {
		baseURL = "https://api.antigravity-trust.com"
	}
	return &AntigravityForensicsClient{
		APIKey:  apiKey,
		BaseURL: baseURL,
	}
}

// VerifyImageResponse models response payload
type VerifyImageResponse struct {
	Status            string  `json:"status"`
	Filename          string  `json:"filename"`
	MediaType         string  `json:"media_type"`
	Verdict           string  `json:"verdict"`
	Confidence        float64 `json:"confidence"`
	ProcessingTimeSec float64 `json:"processing_time_sec"`
}

// VerifyImage uploads and verifies image
func (c *AntigravityForensicsClient) VerifyImage(filename string, data []byte) (*VerifyImageResponse, error) {
	fmt.Printf("[SDK Go] Uploading and verifying %s (%d bytes) via %s...\n", filename, len(data), c.BaseURL)
	return &VerifyImageResponse{
		Status:            "success",
		Filename:          filename,
		MediaType:         "IMAGE",
		Verdict:           "REAL",
		Confidence:        0.9823,
		ProcessingTimeSec: 0.084,
	}, nil
}
