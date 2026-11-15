// INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
// Do not deploy. Do not run against real files.
package download

import (
	"net/http"
	"path/filepath"
)

// Download serves a file from the export directory using the caller's name.
func Download(w http.ResponseWriter, r *http.Request) {
	name := r.URL.Query().Get("file")
	http.ServeFile(w, r, filepath.Join("/var/app/exports", name))
}
