const path = require('path');
const webpack = require('webpack');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = (env, argv) => {
  const isProduction = argv.mode === 'production';

  return {
    entry: './src/index.tsx',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: 'bundle.js',
      publicPath: '/'
    },
    mode: isProduction ? 'production' : 'development',
    devtool: isProduction ? 'source-map' : 'eval-source-map',
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        use: 'ts-loader',
        exclude: /node_modules/
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif)$/i,
        type: 'asset/resource'
      }
    ]
  },
  resolve: {
    extensions: ['.tsx', '.ts', '.js', '.jsx'],
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@components': path.resolve(__dirname, 'src/components'),
      '@agents': path.resolve(__dirname, 'src/agents'),
      '@services': path.resolve(__dirname, 'src/services'),
      '@utils': path.resolve(__dirname, 'src/utils')
    }
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html'
    }),
    new webpack.DefinePlugin({
      NODE_ENV: JSON.stringify(isProduction ? 'production' : 'development'),
      REACT_APP_API_URL: JSON.stringify(process.env.REACT_APP_API_URL || ''),
      REACT_APP_DATA_API_URL: JSON.stringify(process.env.REACT_APP_DATA_API_URL || ''),
      REACT_APP_AGENT_API_URL: JSON.stringify(process.env.REACT_APP_AGENT_API_URL || ''),
      REACT_APP_CHATBOT_API_URL: JSON.stringify(process.env.REACT_APP_CHATBOT_API_URL || ''),
    })
  ],
  devServer: {
    port: 3001,
    historyApiFallback: true,
    hot: true,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:8001',
        changeOrigin: true
      }
    ]
  }
  };
};