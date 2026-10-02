const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

if (fs.existsSync('frontend')) {
  console.log('Building frontend from root directory...');
  execSync('npm run build', { cwd: path.join(__dirname, 'frontend'), stdio: 'inherit' });
  const srcDist = path.join(__dirname, 'frontend', 'dist');
  const targetDist = path.join(__dirname, 'dist');
  if (fs.existsSync(targetDist)) {
    fs.rmSync(targetDist, { recursive: true, force: true });
  }
  fs.cpSync(srcDist, targetDist, { recursive: true });
  console.log('Copied build output to ./dist');
} else {
  console.log('Building frontend inside frontend directory...');
  execSync('npm run build', { stdio: 'inherit' });
}
