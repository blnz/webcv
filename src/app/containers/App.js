import React, { Component, PropTypes } from 'react'
import Provider from 'react-redux';

import { connect } from 'react-redux'
import { browserHistory } from 'react-router'

import {deepOrange500} from 'material-ui/styles/colors';

import getMuiTheme from 'material-ui/styles/getMuiTheme';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import AppBar from 'material-ui/AppBar';
import IconButton from 'material-ui/IconButton';
import MoreVertIcon from 'material-ui/svg-icons/navigation/more-vert';

import IconMenu from 'material-ui/IconMenu';
import MenuItem from 'material-ui/MenuItem';

import { resetErrorMessage } from '../actions'

import MainWidget from './MainWidget';

const styles = {
  container: {
    textAlign: 'center',
    // paddingTop: 200,
  },
};

const muiTheme = getMuiTheme({
  palette: {
    accent1Color: deepOrange500,
  },
});


function noop () {
  console.log("noop()")
}

function refreshUserFeed () {
}

class App extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.handleChange = this.handleChange.bind(this)
  }

  handleChange(nextValue) {
    browserHistory.push(`/${nextValue}`)
  }

  render() {
    const { store, history } = this.props

    var mainMenu = 
      (
	  <IconMenu
	iconButtonElement={
            <IconButton><MoreVertIcon /></IconButton>
	}
	targetOrigin={{horizontal: 'right', vertical: 'top'}}
	anchorOrigin={{horizontal: 'right', vertical: 'top'}}
	  >
          <MenuItem primaryText="Check for new" onTouchTap={(e) => {console.log("We should Refresh"); noop()} }/>
          <MenuItem primaryText="Purge account" onTouchTap={(e) => {console.log("purging"); noop()} }/>
          <MenuItem primaryText="logout" onTouchTap={(e) => {window.location.href = '/logout'} }/>
	  </IconMenu>
      );

    return (
	<div>
	<MuiThemeProvider muiTheme={muiTheme} >
        <div style={styles.container}>
	<AppBar
      title="web Computer Vision"
      iconElementLeft={ <span /> }
      iconElementRight={mainMenu}
        ></AppBar>
      
        <MainWidget/>
        </div>
	</MuiThemeProvider>
	</div>
    );
  }
}


function mapStateToProps(state, ownProps) {
  return {
    errorMessage: state.errorMessage,
    inputValue: ownProps.location.pathname.substring(1)
  }
}

export default connect(mapStateToProps, {
  resetErrorMessage
})(App)
