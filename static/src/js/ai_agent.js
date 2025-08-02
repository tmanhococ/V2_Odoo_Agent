/**
 * AI Agent JavaScript functionality
 */

odoo.define('ai_odoo_agent.ai_agent', function (require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var ajax = require('web.ajax');
    var _t = core._t;

    var AIAgentWidget = Widget.extend({
        template: 'ai_agent_widget',
        
        events: {
            'click .ai-send-btn': '_onSendClick',
            'click .ai-clear-btn': '_onClearClick',
            'keypress .ai-input': '_onInputKeypress',
        },
        
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.conversationLog = '';
        },
        
        start: function () {
            this._super.apply(this, arguments);
            this._setupAutoScroll();
        },
        
        _onSendClick: function (ev) {
            ev.preventDefault();
            this._sendMessage();
        },
        
        _onClearClick: function (ev) {
            ev.preventDefault();
            this._clearConversation();
        },
        
        _onInputKeypress: function (ev) {
            if (ev.which === 13 && !ev.shiftKey) {
                ev.preventDefault();
                this._sendMessage();
            }
        },
        
        _sendMessage: function () {
            var self = this;
            var input = this.$('.ai-input');
            var message = input.val().trim();
            
            if (!message) {
                return;
            }
            
            // Clear input and show loading
            input.val('');
            this._showLoading(true);
            
            // Add user message to log
            this._addToLog('User', message);
            
            // Send to server
            ajax.jsonRpc('/ai_agent/chat', 'call', {
                message: message
            }).then(function (result) {
                self._showLoading(false);
                
                if (result.success) {
                    self._addToLog('Assistant', result.response);
                    self.conversationLog = result.conversation_log;
                } else {
                    self._addToLog('System', 'Error: ' + result.error);
                }
            }).fail(function (error) {
                self._showLoading(false);
                self._addToLog('System', 'Error: ' + error.message);
            });
        },
        
        _clearConversation: function () {
            this.conversationLog = '';
            this.$('.ai-conversation-log').val('');
            this.$('.ai-response').val('');
        },
        
        _addToLog: function (sender, message) {
            var timestamp = new Date().toLocaleTimeString();
            var logEntry = `[${timestamp}] ${sender}: ${message}\n`;
            
            var logField = this.$('.ai-conversation-log');
            var currentLog = logField.val();
            logField.val(currentLog + logEntry);
            
            // Update response field for latest message
            if (sender === 'Assistant') {
                this.$('.ai-response').val(message);
            }
            
            this._scrollToBottom();
        },
        
        _showLoading: function (show) {
            var loadingDiv = this.$('.ai-loading');
            if (show) {
                loadingDiv.show();
            } else {
                loadingDiv.hide();
            }
        },
        
        _setupAutoScroll: function () {
            var self = this;
            this.$('.ai-conversation-log').on('scroll', function () {
                self._scrollToBottom();
            });
        },
        
        _scrollToBottom: function () {
            var logField = this.$('.ai-conversation-log');
            logField.scrollTop(logField[0].scrollHeight);
        }
    });

    // Register the widget
    core.action_registry.add('ai_agent_widget', AIAgentWidget);

    return AIAgentWidget;
}); 