#!/bin/bash
# Netlify build script for debugging

echo "=== Netlify Build Script Starting ==="
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"
echo "Current directory: $(pwd)"
echo "Directory contents:"
ls -la

echo ""
echo "=== Installing dependencies ==="
npm install --legacy-peer-deps || npm install

echo ""
echo "=== Building application ==="
npm run build

echo ""
echo "=== Build complete! Checking dist folder ==="
ls -la dist/

echo "=== Netlify Build Script Complete ==="
