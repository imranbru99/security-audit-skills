// Safe counterpart to vulnerable.go. The requested file must stay under root.
package download

import (
	"errors"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

func underRoot(root, name string) (string, error) {
	if name == "" || strings.ContainsRune(name, 0) {
		return "", errors.New("bad path")
	}
	root = filepath.Clean(root)
	full := filepath.Clean(filepath.Join(root, name))
	rel, err := filepath.Rel(root, full)
	if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(os.PathSeparator)) {
		return "", errors.New("bad path")
	}
	return full, nil
}

// Download serves a file from the export directory using the caller's name.
func Download(w http.ResponseWriter, r *http.Request) {
	full, err := underRoot("/var/app/exports", r.URL.Query().Get("file"))
	if err != nil {
		http.Error(w, "invalid file", http.StatusBadRequest)
		return
	}
	http.ServeFile(w, r, full)
}
