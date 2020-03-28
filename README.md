<div align="center">
    <img src=".github/Fawkes.svg" height="150"/>
    <h1>fawkes</h1>
    <img src="https://img.shields.io/github/v/release/intuit/fawkes" />
    <img src="https://circleci.com/gh/intuit/fawkes.svg?style=svg" alt="fawkes-CircleCI-Status"/>
    <a href="https://codecov.io/gh/intuit/fawkes">
        <img src="https://codecov.io/gh/intuit/fawkes/branch/master/graph/badge.svg" />
    </a>
    <a href="https://github.com/pre-commit/pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" alt="pre-commit" style="max-width:100%;">
    </a>
    <img src="https://img.shields.io/badge/python-3.7-blue" />
    <img src="https://img.shields.io/badge/contributions-welcome-orange" />
</div>
<h2>What's fawkes ?</h2>
<p>
    Fawkes is a platform designed for product-managers as well as product development teams to get a consolidated view on how well the product is doing from a customer perspective, getting the top issues that the customers are talking about, their sentiments and how they are feeling about the product.
</p>
<h2>Architecture</h2>
<div align="center">
    <img src=".github/Fawkes-Architecture.svg"/>
</div>
<h2>Features</h2>
<ul>
    <li>🚀 Integration with multiple data source</li>
    <li>⚡️ Kibana dashboard for searching and filtering data</li>
    <li>💎 Simple, Configurable and Powerful</li>
    <li>🔥 Built entirely using open-source tools</li>
</ul>
<h2>Onboarding</h2>
<ul>
    <li>Fork this repo</li>
    <li>Add your app's config in the <tr><td><a href="/app/"><code>app/</code></a> folder. Look at the sample configs for reference.
    <li>Enable <tr><td><a href="https://circleci.com/">CircleCI</a> for your application</li>
    <li>🎉🎊 That's All 🎉🎊
</ul>
<h2>Configuration</h2>
<ul>
    <li>
        Create a config file for your app. If your app name is mint, create a file like <tr><td><a href="app/sample-mint-config.json"><code>app/sample-mint-config.json</code></a>
    </li>
    <li>
        There are some app level configs.
    </li>
    <li>To add user feedbacks/verbatims from a channel, we need to add an entry into <code>review-channels</code> array.
</ul>
<h3>App. level configs</h3>

<table>
    <tr>
        <th>Config Key Name</th>
        <th>Description</th>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>app</code></a></td>
        <td>App. Name</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>elastic-search-index</code></a></td>
        <td>The elastic search index to upload data to.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>lifetime-rating-elastic-search-index</code></a></td>
        <td>The elastic search index to upload the lifetime ratings. It needs to uploaded to a different index because it does not follow the lifecycle of a normal REVIEW.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>app-logo</code></a></td>
        <td>The URL for the logo of the app.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>email-time-span</code></a></td>
        <td>The time filter in days to use for sending summary emails.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>bug-feature-file</code></a></td>
        <td>The file which contains the weight and keywords for categorizing the user feedback to bugs/features.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>topic-keywords-file</code></a></td>
        <td>The file which contains the weight and keywords for categorizing the user feedback to different categories.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>algorithm-days-filter</code></a></td>
        <td>The filter in days to apply to filter out the feedbacks. This will be applied while parsing, running algorithms etc.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>email-subject-name</code></a></td>
        <td>The subject name for the summary emails.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>email-list</code></a></td>
        <td>The list of email addresses to send the summary email.</td>
    <tr>
        <td><a href="#app-level-configs"><code>sendgrid-api-key</code></a></td>
        <td>We use <a href="https://sendgrid.com/">Sendgrid</a> to send emails.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>slackbot-run-interval</code></a></td>
        <td>The time interval to filter the feedbacks to send to the slack channel.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>slack-hook-url</code></a></td>
        <td>The slack web-hook used to send the slack notifications.</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>slack-channel</code></a></td>
        <td>The name of the slack channel</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>jira</code></a></td>
        <td>Coming Soon!</td>
    </tr>
    <tr>
        <td><a href="#app-level-configs"><code>review-channels</code></a></td>
        <td>List of channel configs.</td>
    </tr>
</table>
<h2>Contributing</h2>
For details on how to contribute to this project see <a href=".github/CONTRIBUTING.md">CONTRIBUTING.md</a>
