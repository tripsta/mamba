# Watchr can be used to automatically run only necessary tests on file save.
# This script will detect changes in:
#   - all files in 'tests/' with extension 'php'
#   - all files in 'library/TP24' with extension 'php'
#   - all files in 'application/' with extension 'php' (models, controllers, helpers)
#
# One limitation is lack of support for view tests (since mappings between
# corresponding view and test files are hard to describe in regex).
#
#
# To install, run:
#
#   $ gem install watchr
#   $ gem install notifier
#
# for windows also run $ gem install win32-open3, Install Snarl: download from www.fullphat.net, $ gem install ruby-snarl
#
# To run the script, do:
#
#   $ watchr tests/watchr.rb

require 'rubygems'
require 'notifier'

if RUBY_PLATFORM.include? 'w32'
  require 'win32/open3'
else
  require 'open3'
end

watch '^pythepie/tests/(.*)\.py$' do |match|
  unittest(match[0])
  say "waiting..."
end

watch '^pythepie/app/(.*)\.py$' do |match|
  dir_separator = '/'
  folder_and_file = match[1].split(dir_separator)
  file = folder_and_file.pop
  folder = folder_and_file.join(dir_separator)
  test_file = "pythepie/tests/#{folder}/test_#{file}.py"
  print test_file
  unittest(test_file)
  say "waiting..."
end

def say what
  puts "\n   [#{Time.now.strftime('%H:%M:%S')}] #{what}\n"
end


def unittest file
  if File.exists? file
    cmd = "trial #{file} 2>&1"
    say "About to run `#{cmd}`"
    _, out, _ = Open3.popen3(cmd)

    previous = last = nil

    until out.eof?
      previous = last
      puts last = out.gets
    end

    file_name = File.basename(file)
    image, summary, message = case
    when last =~ /\APASSED(.*)/
      ['dialog-ok', file_name, last.gsub('OK (', '').gsub(')', '')]
    else
      ['dialog-warning', previous, last]
    end

    notify image, summary, message
  end
end

def notify image, summary, message
  Notifier.notify :image => image, :title => summary, :message => message
end
