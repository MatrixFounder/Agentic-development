# Go Developer Guidelines

## Core Principles
- **Idiomatic Go:** Follow "Effective Go". Simple, explicit, readable code.
- **Error Handling:** treat errors as values.
    - **Wrapping:** Use `fmt.Errorf("context: %w", err)` to add context.
    - **Checking:** Use `errors.Is(err, target)` instead of `==`.
- **Formatting:** `gofmt` is non-negotiable. Use `goimports` for import management.

## Project Structure (Standard)
- **Layout:**
    - `cmd/`: Entry points (main packages).
    - `internal/`: Private library code.
    - `pkg/`: Public library code (rarely needed, prefer internal).
- **Modules:** Use `go.mod` for dependency management.

## Concurrency
- **Channels vs Mutex:** "Share memory by communicating". Use channels for data flow, Mutex for state synchronization.
- **Context:** ALWAYS propagate `context.Context` as the first argument in long-running or I/O functions.
- **ErrGroup:** Use `golang.org/x/sync/errgroup` for managing multiple goroutines (replaces `WaitGroup` + error channel).

## Testing
- **Table-Driven Tests:** Standard pattern for all logic tests.
    ```go
    tests := []struct{ name, input, want }{ ... }
    for _, tt := range tests { t.Run(tt.name, ...) }
    ```
- **Fuzzing:** Use native `go test -fuzz` (Go 1.18+).

## Tooling
- **Linting:** Use `golangci-lint` with standard presets.
- **Vulnerabilities:** run `govulncheck ./...`.

## Specific Contexts (Scripts / Single File)
- **Start Small:** `package main` in a single file is fine for scripts.
- **No `go.mod`?**: Not recommended, but possible with `GO111MODULE=off` or simple `go run script.go`.
- **Dependencies:** For scripts with deps, considering using **GoReleaser** or just a Makefile to ensure reproducibility.
- **Shebang:** Go does not support shebang `#!/usr/bin/env go run` natively across all OSs easily, prefer explicit `go run`.
